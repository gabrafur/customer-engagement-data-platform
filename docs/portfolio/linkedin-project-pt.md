# Projeto no LinkedIn

## Título do projeto

Plataforma de Dados para Customer Engagement | PySpark, Delta Lake & Databricks

## Descrição curta

Projeto independente de engenharia de dados, inspirado em práticas de produção, que
demonstra feature engineering com PySpark, padrões de idempotência com Delta Lake, entrega
confiável, replay histórico, observabilidade, testes e empacotamento compatível com
Databricks usando dados sintéticos.

## Descrição do projeto

Desenvolvi uma plataforma independente e reproduzível localmente para processar dados
sintéticos de clientes e transações com Python, a API DataFrame do PySpark, expressões Spark
SQL e padrões Delta Lake. O pipeline produz recomendações validadas, pontuadas, ranqueadas e
armazenadas com semântica idempotente.

O repositório evidencia decisões para além do happy path: quality gates obrigatórios,
ordenação determinística, retries limitados, estados explícitos de esgotamento, reconciliação,
reprocessamento as-of sem efeitos externos, modelo de transactional outbox, utilitários de
execução em DAG, proveniência, logs estruturados e métricas de execução. A CI automatizada
valida tipagem estrita, lint, 52 testes — incluindo Spark local —, cobertura medida de 96,9%,
build do wheel e segurança de conteúdo.

A execução local é a referência reproduzível. O adaptador Delta MERGE e o Databricks Asset
Bundle são exemplos verificáveis de compatibilidade; o projeto não afirma operar uma workload
real em produção nem possuir um workspace ativo.

## Tecnologias

Python · PySpark · Apache Spark · API DataFrame do PySpark · expressões Spark SQL · Delta
Lake · SQL · YAML · TOML · pytest · GitHub Actions · Databricks Asset Bundles

## Competências sugeridas no LinkedIn

- Databricks
- Apache Spark
- PySpark
- Python
- SQL
- Delta Lake
- Engenharia de Dados
- Pipelines de Dados
- Arquitetura de Dados
- CI/CD

## Repositório

https://github.com/gabrafur/customer-engagement-data-platform
