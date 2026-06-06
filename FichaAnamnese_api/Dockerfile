# Imagem base leve
FROM python:3.11-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala dependências primeiro
# (aproveita cache do Docker se requirements não mudar)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Porta que a API vai expor
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]