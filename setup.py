from distutils.core import setup

setup(
    name="veritas",
    version="1.0.3",
    description="Python tablular information manipulation library",
    author="Anthony Post",
    author_email="postanthony3000@gmail.com",
    url="https://github.com/Ayehavgunne/veritas/",
    packages=["veritas"],
    extras_require={
        "dist": ["dateutil", "BeautifulSoup4"],
        "dev": ["pytest", "pylint"],
    },
)
