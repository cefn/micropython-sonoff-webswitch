"""
    OTA Client for micropython devices
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Connect to OTA Server and run commands from him
    to update local files.

    This script must be run on the micropython device.
"""
import gc
import sys

import machine
import network
import ubinascii as binascii
import uhashlib as hashlib
import uos as os
import usocket as socket
import utime as time

SOCKET_TIMEOUT = const(10)
PORT = const(8266)
CHUNK_SIZE = const(512)
ENCODING = 'utf-8'
BUFFER = bytearray(CHUNK_SIZE)
FILE_TYPE = const(0x8000)


def reset():
    for no in range(3, 1, -1):
        print('Hard reset device in %i sec...' % no)
        time.sleep(1)
    machine.reset()
    time.sleep(1)
    sys.exit()


class OtaClient:
    def __init__(self, server_socket):
        self.server_socket = server_socket

    def run(self):
        self.server_socket.settimeout(SOCKET_TIMEOUT)

        last_error = None
        while True:
            print('\nwait for command...', end='')
            command = self.read_line_string()
            if not command:
                self.server_socket.sendall(b'Get empty command: Abort.')
                break

            print('Receive command:', command)
            if command == 'exit':
                print('exit!')
                self.command_send_ok()
                break

            gc.collect()

            try:
                func = getattr(self, 'command_%s' % command)
            except AttributeError:
                self.server_socket.sendall(b'Command unknown!')
            else:
                try:
                    func()
                except Exception as e:
                    print('Error running command:')
                    sys.print_exception(e)
                    last_error = str(e)

            gc.collect()
            print('Send new line: Command ends.')
            self.server_socket.sendall(b'\n')

        if last_error:
            raise AssertionError(last_error)

        return 'OK'

    def read_line_bytes(self):
        gc.collect()
        line_bytes = self.server_socket.readline()
        if not line_bytes:
            return b''
        if not line_bytes.endswith(b'\n'):
            raise AssertionError('Byte line not terminated:', repr(line_bytes))
        return line_bytes[:-1]

    def read_line_string(self):
        return self.read_line_bytes().decode(ENCODING)

    def command_send_ok(self, terminated=False):
        self.server_socket.sendall(b'OK')
        if terminated:
            self.server_socket.sendall(b'\n')

    def command_chunk_size(self):
        """
        Send our chunk size in bytes.
        """
        self.server_socket.sendall(b'%i' % CHUNK_SIZE)

    def command_files_info(self):
        for name, file_type, inode, size in os.ilistdir():
            if file_type != FILE_TYPE:
                print(' *** Skip: %s' % name)
                continue

            self.server_socket.sendall(b'%s\r%i\r' % (name, size))

            sha256 = hashlib.sha256()
            with open(name, 'rb') as f:
                while True:
                    count = f.readinto(BUFFER, CHUNK_SIZE)
                    if count < CHUNK_SIZE:
                        sha256.update(BUFFER[:count])
                        break
                    else:
                        sha256.update(BUFFER)

            self.server_socket.sendall(binascii.hexlify(sha256.digest()))
            self.server_socket.sendall(b'\r\n')
        self.server_socket.sendall(b'\n\n')

    def command_receive_file(self):
        """
        Store a new/updated file on local micropython device.
        """
        print('receive file', end=' ')
        file_name = self.read_line_string()
        print(file_name)
        file_size = int(self.read_line_string())
        print('%i Bytes' % file_size)
        file_sha256 = self.read_line_string()
        print('SHA256: %r' % file_sha256)
        self.command_send_ok(terminated=True)

        temp_file_name = '%s.temp' % file_name
        print('Create %s' % temp_file_name)
        try:
            with open(temp_file_name, 'wb') as f:
                print('receive data', end='')
                sha256 = hashlib.sha256()
                received = 0
                while True:
                    if received + CHUNK_SIZE > file_size:
                        size = file_size - received
                        if size == 0:
                            break
                    else:
                        size = CHUNK_SIZE

                    count = self.server_socket.readinto(BUFFER, size)
                    print('.', end='')

                    received += count
                    if received >= file_size:
                        f.write(BUFFER[:count])
                        sha256.update(BUFFER[:count])
                        print('completed')
                        break

                    f.write(BUFFER)
                    sha256.update(BUFFER)

            print('Received %i Bytes' % received, end=' ')

            local_file_size = os.stat(temp_file_name)[6]
            print('Written %i Bytes' % local_file_size)
            if local_file_size != file_size:
                print('Size error!')
                self.server_socket.sendall(b'Size error!\n')
                raise AssertionError('Size error!')

            hexdigest = binascii.hexlify(sha256.digest()).decode(ENCODING)
            if hexdigest == file_sha256:
                print('Hash OK:', hexdigest)
                print('Replace old file.')
                try:
                    os.remove(file_name)
                except OSError:
                    pass  # e.g.: new file that doesn't exist, yet.

                os.rename(temp_file_name, file_name)

                print('Compare written file content...')
                sha256 = hashlib.sha256()
                with open(file_name, 'rb') as f:
                    while True:
                        count = f.readinto(BUFFER, CHUNK_SIZE)
                        if count < CHUNK_SIZE:
                            sha256.update(BUFFER[:count])
                            break
                        else:
                            sha256.update(BUFFER)

                hexdigest = binascii.hexlify(sha256.digest()).decode(ENCODING)
                if hexdigest == file_sha256:
                    print('Hash OK:', hexdigest)
                    self.command_send_ok()
                    return

            print('Hash Error:', hexdigest)
            self.server_socket.sendall(b'Hash error!\n')
            raise AssertionError('Hash error!')
        finally:
            print('Remove temp file')
            try:
                os.remove(temp_file_name)
            except OSError:
                pass


def get_active_wlan():
    for interface_type in (network.AP_IF, network.STA_IF):
        wlan = network.WLAN(interface_type)
        if wlan.active():
            return wlan
    raise RuntimeError('WiFi not active!')


def discovery_ota_server():
    gc.collect()
    own_ip = get_active_wlan().ifconfig()[0]
    print('Own IP:', own_ip)
    ip_prefix = own_ip.rsplit('.', 1)[0]

    for timeout in (0.15, 0.3, 0.5):
        print('\nScan: %s.X with timeout: %s' % (ip_prefix, timeout), end='')
        for no in range(1, 255):
            gc.collect()
            server_address = ('%s.%i' % (ip_prefix, no), PORT)
            print('.', end='')

            sock = socket.socket()
            sock.settimeout(timeout)
            try:
                sock.connect(server_address)
            except OSError:
                sock.close()
            else:
                print('\nFound OTA Server at: %s:%s' % server_address)
                return sock

    raise RuntimeError('OTA Server not found!')


def do_ota_update():
    server_socket = discovery_ota_server()
    gc.collect()
    try:
        return OtaClient(server_socket).run()
    except Exception as e:
        sys.print_exception(e)
        reset()
    finally:
        server_socket.close()


if __name__ == '__main__':
    print(do_ota_update())
    reset()
