"""Testar código assíncrono sem plugins: asyncio.run e unittest.IsolatedAsyncioTestCase."""
import asyncio
import unittest


async def fetch_user(user_id, delay=0.01):
    await asyncio.sleep(delay)
    if user_id < 0:
        raise ValueError("id inválido")
    return {"id": user_id}


class FetchTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.users = await asyncio.gather(fetch_user(1), fetch_user(2))

    async def test_gather(self):
        self.assertEqual([u["id"] for u in self.users], [1, 2])

    async def test_error(self):
        with self.assertRaises(ValueError):
            await fetch_user(-1)

    async def test_timeout(self):
        with self.assertRaises(TimeoutError):
            async with asyncio.timeout(0.01):
                await fetch_user(1, delay=1)


def test_with_plain_asyncio_run():
    """Em pytest puro: uma função comum que chama asyncio.run (nenhum plugin)."""
    assert asyncio.run(fetch_user(7)) == {"id": 7}


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
    test_with_plain_asyncio_run()
    print("test_with_plain_asyncio_run: passou (pytest-asyncio e anyio automatizam isto, mas não são obrigatórios)")
