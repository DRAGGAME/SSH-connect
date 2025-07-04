import asyncio
import logging
import os

from dotenv import load_dotenv
import asyncssh
logging.basicConfig(level=logging.WARNING)
logging.basicConfig(level=logging.WARN)
logging.basicConfig(level=logging.ERROR)
load_dotenv()
host = os.getenv('host')
name = os.getenv('name')
password = os.getenv('password')

docker_adm = os.getenv('docker_adm')
docker_client = os.getenv('docker_client')

async def main():
    async with asyncssh.connect(host, username=name, password=password) as conn:
        print('Удаление старых файлов')
        await conn.run('rm -f /home/tgadm.tar /home/tgclient.tar', check=True)
        await conn.run('rm -f /home/tgadm.tar', check=True)

        print("Загрузка образов")
        async with conn.start_sftp_client() as sftp:
            await sftp.put('tgadm.tar', '/home')
            await sftp.put('tgclient.tar', '/home')

        print('Удаление старых образов')
        await conn.run('docker stop tgadm || true && docker rm tgadm || true && docker image rm draggame023/tgadm:latest || true', check=True)
        await conn.run('docker stop tgclient || true && docker rm tgclient || true && docker image rm draggame023/tgclient:latest || true', check=True)

        print("Загрузка самих образов")
        await conn.run('docker load < /home/tgadm.tar', check=True)
        await conn.run('docker load < /home/tgclient.tar', check=True)

        print('Запуск образов')
        if docker_adm:
            await conn.run(docker_adm, check=True)
        if docker_client:
            await conn.run(docker_client, check=True)

        print("Завершение")

asyncio.run(main())
