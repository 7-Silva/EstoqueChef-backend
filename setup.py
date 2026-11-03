from setuptools import find_packages, setup


def ler_requisitos(arquivo="requirements.txt"):
    with open(arquivo, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith(("#", "-r"))]


setup(
    name="estoquechef",
    version="1.0.0",
    description="API de controle de estoque para restaurantes e confeitarias",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.10.6",
    install_requires=ler_requisitos(),
    entry_points={"console_scripts": ["estoquechef = estoquechef.cli:main"]},
)
