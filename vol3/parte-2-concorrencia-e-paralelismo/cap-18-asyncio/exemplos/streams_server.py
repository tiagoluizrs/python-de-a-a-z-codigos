"""Um servidor TCP e centenas de clientes em UMA thread."""
import asyncio
import time


async def handle(reader, writer):
    line = await reader.readline()
    writer.write(line.upper())
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def client(port, i):
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(f"ola {i}\n".encode())
    await writer.drain()
    reply = await reader.readline()
    writer.close()
    await writer.wait_closed()
    return reply.decode().strip()


async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 0, backlog=1024)    # fila de conexões pendentes (padrão: 100)
    port = server.sockets[0].getsockname()[1]
    async with server:
        for n in (50, 200, 500):
            start = time.perf_counter()
            replies = await asyncio.gather(*(client(port, i) for i in range(n)))
            elapsed = time.perf_counter() - start
            assert replies[3] == "OLA 3"
            print(f"{n:>4} clientes conectam, enviam e recebem: {elapsed * 1e3:7.0f} ms ({elapsed / n * 1e3:.2f} ms por cliente)")
        server.close()
    print("servidor e clientes no MESMO laço, uma thread só")


asyncio.run(main())
