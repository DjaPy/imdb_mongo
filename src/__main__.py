from aiomisc import entrypoint

if __name__ == '__main__':
    with entrypoint() as loop:
        loop.run_forever()
