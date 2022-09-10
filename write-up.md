# Writeup for the first challenge on Pwnable.tw: Start

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

`mov bl, 0x14`: size of the string it wants to print.

`mov ecx, esp`: exc will hold "Let's start the CTF:" from now on and parse to write() as `const void *buf`.

- _0x08048091_ - _0x08048097_: This time, the al is set to 3, which means it wants to call sys_read.

`ssize_t read(int fd, void *buf, size_t count);`

`read() attempts to read up to count bytes from file descriptor fd into the buffer starting at buf.`

_read(2) - Linux manual page_

`XOR ebx, ebx`: Clean up register.

`mov dl, 0x3C`: Read 60 bytes from STDINT.

