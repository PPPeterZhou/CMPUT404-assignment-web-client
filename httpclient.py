#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.splitlines()[0].split()[1])

    def get_headers(self,data):
        header = ""
        header_list = data.split("\r\n\r\n")[0].split("\r\n")[1:]
        for item in header_list:
            header += (item + "\r\n")
        header += "\r\n"
        return header
        

    def get_body(self, data):
        return (data.split("\r\n\r\n")[1])
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # Deafault settings
        code = 500
        body = ""
        port = 80
        path = "/"
        
        # parse the url
        url_parsed = urlparse(url)
        
        # get host
        host = url_parsed.hostname

        # Set port if port is specified
        if url_parsed.port:
            port = url_parsed.port
        
        # Set path if path is specified
        if url_parsed.path != "":
            path = url_parsed.path

        # Set query if query is specified
        if url_parsed.query != "":
            path += ("?" + url_parsed.query)

        self.connect(host, port)

        # Request Format
        # GET {path} HTTP/1.1
        # Host: {host}
        # Accept: */* (all media types)
        # Connection: close
        request = "GET {fpath} HTTP/1.1\r\nHost: {fhost}\r\nAccept: */*\r\nConnection: close\r\n\r\n".format(fpath=path, fhost=host)

        # send request and receive response
        self.sendall(request)
        response = self.recvall(self.socket)

        # Get the code and body from response
        code = self.get_code(response)
        body = self.get_body(response)

        # close socket
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Deafault settings
        code = 500
        body = ""
        port = 80
        path = "/"
        content = ""
        content_length = 0
        content_type = "application/x-www-form-urlencoded"
        temp = 0

        # parse the url
        url_parsed = urlparse(url)

        # get host
        host = url_parsed.hostname

        # Set port if port is specified
        if url_parsed.port:
            port = url_parsed.port
        
        # Set path if path is specified
        if url_parsed.path != "":
            path = url_parsed.path

        # Set args if args is not empty
        if args:
            for k, v in args.items():
                if temp != 0:
                    content += "&"
                content += ("{key}={value}").format(key=k, value=v)
                temp += 1
            content_length = len(content)

        self.connect(host, port)

        # Request Format
        # POST {file} HTTP/1.1
        # Host: {host}
        # Content-Type: application/x-www-form-urlencoded (By Default)
        # Content-Length: int
        # 
        # Content
        request = "POST {fpath} HTTP/1.1\r\nHost: {fhost}\r\nContent-Type: {fCType}\r\nContent-Length: {fCLength}\r\n\r\n{fC}\r\n\r\n".format(fpath=path, fhost=host, fCType=content_type, fCLength=content_length, fC=content)
        
        # send request and receive response
        self.sendall(request)
        response = self.recvall(self.socket)

        # Get the code and body from response
        code = self.get_code(response)
        body = self.get_body(response)

        # close socket
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
