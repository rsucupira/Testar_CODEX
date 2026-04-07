# Testar_CODEX

## Modelo para simular investimento em FIDC (Sênior e Mezanino)

Este repositório contém um simulador didático de fluxo de caixa mensal para FIDC com duas classes de cotas:
- **Sênior** (com prioridade de pagamento e retorno alvo).
- **Mezanino** (absorve o residual positivo/negativo após a Sênior).

Arquivo principal: `fidc_simulator.py`.

## Como o modelo funciona

A cada mês, o simulador:
1. Calcula o **ganho bruto** da carteira.
2. Desconta **inadimplência**.
3. Desconta **taxa de administração**.
4. Distribui o resultado disponível por regra de waterfall:
   - paga a cota **Sênior** até o retorno alvo mensal;
   - o **residual** vai para a cota Mezanino.

> É um modelo simplificado para estudo/sensibilidade, não substitui estruturação jurídica, contábil e regulatória de um FIDC real.

## Como executar

Pré-requisito: Python 3.10+.

```bash
python3 fidc_simulator.py
```

Isso executa com parâmetros padrão e gera `resultado_fidc.csv`.

## Principais parâmetros

```bash
python3 fidc_simulator.py \
  --meses 36 \
  --senior-inicial 10000000 \
  --mezanino-inicial 3000000 \
  --retorno-carteira-anual 0.20 \
  --retorno-senior-anual 0.15 \
  --inadimplencia-mensal 0.012 \
  --taxa-adm-anual 0.02 \
  --csv cenario_base.csv
```

### Significado dos parâmetros
- `--meses`: horizonte da simulação.
- `--senior-inicial`: patrimônio inicial da tranche Sênior.
- `--mezanino-inicial`: patrimônio inicial da tranche Mezanino.
- `--retorno-carteira-anual`: retorno bruto anual dos recebíveis/carteira.
- `--retorno-senior-anual`: retorno alvo anual da Sênior (prioritário).
- `--inadimplencia-mensal`: perdas mensais da carteira.
- `--taxa-adm-anual`: taxa de administração anual.
- `--csv`: caminho do arquivo de saída com histórico mensal.

## Como analisar o resultado

O script imprime um resumo final no terminal e salva um CSV com colunas como:
- `resultado_disponivel`
- `pagamento_senior`
- `pagamento_mezanino`
- `saldo_senior`
- `saldo_mezanino`
- `patrimonio_final`

Com isso você consegue:
- comparar cenários de inadimplência;
- testar se o retorno da carteira suporta a meta da Sênior;
- medir sensibilidade do retorno Mezanino (tranche de maior risco).
