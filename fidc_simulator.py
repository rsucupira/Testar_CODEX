#!/usr/bin/env python3
"""Simulador simples de FIDC com cotas Sênior e Mezanino.

Modelo de caixa mensal:
1) Aplica rentabilidade bruta da carteira.
2) Desconta perdas (inadimplência).
3) Paga taxa de administração.
4) Distribui resultado por prioridade:
   - Cota Sênior recebe retorno alvo (até o limite do caixa).
   - Cota Mezanino recebe o residual.

Observação: este é um modelo didático para sensibilidade/planejamento.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Tranche:
    nome: str
    saldo: float
    retorno_alvo_anual: float

    @property
    def retorno_alvo_mensal(self) -> float:
        return (1 + self.retorno_alvo_anual) ** (1 / 12) - 1


@dataclass
class SimulacaoConfig:
    meses: int
    retorno_carteira_anual: float
    inadimplencia_mensal: float
    taxa_adm_anual: float

    @property
    def retorno_carteira_mensal(self) -> float:
        return (1 + self.retorno_carteira_anual) ** (1 / 12) - 1

    @property
    def taxa_adm_mensal(self) -> float:
        return (1 + self.taxa_adm_anual) ** (1 / 12) - 1


def simular_fidc(senior: Tranche, mezanino: Tranche, cfg: SimulacaoConfig) -> list[dict]:
    historico: list[dict] = []

    for mes in range(1, cfg.meses + 1):
        patrimonio_inicio = senior.saldo + mezanino.saldo

        ganho_bruto = patrimonio_inicio * cfg.retorno_carteira_mensal
        perda_inadimplencia = patrimonio_inicio * cfg.inadimplencia_mensal
        taxa_adm = patrimonio_inicio * cfg.taxa_adm_mensal

        resultado_disponivel = ganho_bruto - perda_inadimplencia - taxa_adm

        target_senior = senior.saldo * senior.retorno_alvo_mensal
        pagamento_senior = min(max(resultado_disponivel, 0.0), target_senior)

        residual = resultado_disponivel - pagamento_senior
        pagamento_mezanino = residual

        senior.saldo += pagamento_senior
        mezanino.saldo += pagamento_mezanino

        historico.append(
            {
                "mes": mes,
                "patrimonio_inicio": patrimonio_inicio,
                "ganho_bruto": ganho_bruto,
                "perda_inadimplencia": perda_inadimplencia,
                "taxa_adm": taxa_adm,
                "resultado_disponivel": resultado_disponivel,
                "target_senior": target_senior,
                "pagamento_senior": pagamento_senior,
                "pagamento_mezanino": pagamento_mezanino,
                "saldo_senior": senior.saldo,
                "saldo_mezanino": mezanino.saldo,
                "patrimonio_final": senior.saldo + mezanino.saldo,
            }
        )

    return historico


def exportar_csv(historico: list[dict], caminho: Path) -> None:
    if not historico:
        return

    campos = list(historico[0].keys())
    with caminho.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(historico)


def formatar_percentual(x: float) -> str:
    return f"{100*x:.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulador de FIDC (Sênior + Mezanino)")
    parser.add_argument("--meses", type=int, default=24, help="Horizonte da simulação em meses")
    parser.add_argument("--senior-inicial", type=float, default=8_000_000, help="Saldo inicial da cota Sênior")
    parser.add_argument("--mezanino-inicial", type=float, default=2_000_000, help="Saldo inicial da cota Mezanino")
    parser.add_argument("--retorno-carteira-anual", type=float, default=0.18, help="Retorno bruto anual da carteira")
    parser.add_argument("--retorno-senior-anual", type=float, default=0.14, help="Retorno alvo anual da cota Sênior")
    parser.add_argument("--retorno-mezanino-anual", type=float, default=0.0, help="Retorno alvo anual da cota Mezanino (informativo)")
    parser.add_argument("--inadimplencia-mensal", type=float, default=0.01, help="Perda mensal por inadimplência")
    parser.add_argument("--taxa-adm-anual", type=float, default=0.02, help="Taxa anual de administração")
    parser.add_argument("--csv", type=Path, default=Path("resultado_fidc.csv"), help="Arquivo CSV de saída")

    args = parser.parse_args()

    senior = Tranche("Senior", args.senior_inicial, args.retorno_senior_anual)
    mezanino = Tranche("Mezanino", args.mezanino_inicial, args.retorno_mezanino_anual)
    cfg = SimulacaoConfig(
        meses=args.meses,
        retorno_carteira_anual=args.retorno_carteira_anual,
        inadimplencia_mensal=args.inadimplencia_mensal,
        taxa_adm_anual=args.taxa_adm_anual,
    )

    historico = simular_fidc(senior, mezanino, cfg)
    exportar_csv(historico, args.csv)

    fim = historico[-1]
    total_inicio = args.senior_inicial + args.mezanino_inicial
    total_fim = fim["patrimonio_final"]
    retorno_total = total_fim / total_inicio - 1

    print("=== Resumo da Simulação FIDC ===")
    print(f"Meses: {args.meses}")
    print(f"Patrimônio inicial: R$ {total_inicio:,.2f}")
    print(f"Patrimônio final:   R$ {total_fim:,.2f}")
    print(f"Retorno total:      {formatar_percentual(retorno_total)}")
    print(f"Saldo final Senior:   R$ {fim['saldo_senior']:,.2f}")
    print(f"Saldo final Mezanino: R$ {fim['saldo_mezanino']:,.2f}")
    print(f"CSV salvo em: {args.csv}")


if __name__ == "__main__":
    main()
