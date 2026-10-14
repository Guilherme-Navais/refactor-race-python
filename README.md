# REFactor Race Python

## EQUIPE
- Guilherme de Oliveira Navais - 4251923674
- Anthony Rafael Braga Magalhães - 4251924039

## DESCRIÇÃO
Projeto de refatoração, testes automatizados e análise de qualidade de software aplicado a um módulo legado de processamento de pedidos (`legacy_checkout.py`), buscando reduzir a complexidade ciclomática e aumentar a manutenibilidade preservando 100% do comportamento original.

## DIAGNÓSTICO INICIAL
1. **Função monolítica (`process_order`):** Concentrava cálculo de subtotal, descontos por perfil, cupons, frete, impostos, fidelidade, detecção de duplicatas, persistência em lista global e impressão no console.
2. **Duplicação de código:** O subtotal era calculado duas vezes seguidas (`total1` e `subtotal`) com a mesma lógica.
3. **Alta complexidade ciclomática:** Múltiplos blocos `if/else` profundamente aninhados dificultavam a leitura e o teste isolado das regras.
4. **Ineficiência algorítmica:** A verificação de produtos duplicados usava dois loops aninhados $O(n^2)$ com três níveis de `if`.
5. **Problemas apontados na análise estática (Ruff):** Comparações explícitas com booleanos (`express == False` e `express == True` - regra `E712`) e variável não utilizada (`total1`).

## CODE SMELLS ENCONTRADOS
- **Long Method / God Function:** A função `process_order` realizava todas as etapas do domínio de negócio e efeitos colaterais.
- **Duplicate Code:** Cálculo redundante do subtotal na variável `total1`.
- **Magic Numbers & Magic Strings:** Valores como `0.15`, `0.25`, `1.8`, `1000`, `500` e siglas de estados espalhados diretamente nas condicionais.
- **Deeply Nested Conditionals:** Uso de `else: if ... else: if ...` em vez de `elif` ou *early returns* no cálculo de desconto.
- **Poor Naming:** Variáveis genéricas ou misturando idiomas sem padrão (`x`, `total1`, `taxa`).
- **Global State & Side Effects:** Acoplamento direto com a lista global `ORDERS_PROCESSED` e chamadas `print()` dentro da função principal.

## REFATORAÇÕES REALIZADAS

### 1. Extração de Funções Especializadas (*Extract Function*)
- **Problema encontrado:** `process_order` possuía alta complexidade ciclomática e múltiplas responsabilidades.
- **Alteração realizada:** Extração das funções `calculate_subtotal`, `calculate_customer_discount`, `calculate_coupon_discount`, `calculate_discount`, `calculate_shipping`, `calculate_tax`, `calculate_loyalty_points`, `find_duplicate_products` e `print_order_summary`.
- **Justificativa:** Reduz a complexidade de `process_order` para `A (1)` no Radon, isola regras de negócio e permite testar cada regra individualmente.

### 2. Remoção de Código Duplicado e Variáveis Mortas (*Remove Duplicate Code*)
- **Problema encontrado:** O loop de cálculo de `total1` era idêntico ao de `subtotal` e seu valor nunca era lido.
- **Alteração realizada:** Remoção de `total1` e consolidação do cálculo em uma *generator expression* com `sum()`.
- **Justificativa:** Elimina processamento redundante em tempo de execução e melhora a legibilidade.

### 3. Substituição de Condicionais por Mapeamento e Conjuntos (*Replace Conditional with Mapping / Simplify Conditional*)
- **Problema encontrado:** Sequência extensa de `if/elif` para alíquotas de impostos por estado e múltiplos `or` para verificar estados do Sudeste.
- **Alteração realizada:** Criação do dicionário `TAX_RATES` consultado via `.get(state, DEFAULT_TAX_RATE)` e do conjunto `SOUTHEAST_STATES = {"MG", "SP", "RJ", "ES"}`.
- **Justificativa:** Reduz ramificações condicionais (diminuindo a complexidade ciclomática) e torna a busca $O(1)$.

### 4. Substituição de Números Mágicos por Constantes (*Replace Magic Number with Constant*)
- **Problema encontrado:** Percentuais de desconto, limites de frete grátis e multiplicadores estavam fixos no meio das fórmulas.
- **Alteração realizada:** Extração de constantes semânticas no topo do módulo (ex: `MAX_DISCOUNT_RATE = 0.25`, `EXPRESS_SHIPPING_MULTIPLIER = 1.8`).
- **Justificativa:** Evita erros de manutenção e documenta o significado de cada valor de negócio.

### 5. Otimização da Busca de Produtos Duplicados (*Algorithm Optimization*)
- **Problema encontrado:** Loop duplo $O(n^2)$ comparando índices `i` e `j` para achar nomes repetidos.
- **Alteração realizada:** Uso de `collections.Counter` para contar ocorrências em tempo linear $O(n)$.
- **Justificativa:** Reduz drasticamente o número de comparações e elimina 4 níveis de indentação, mantendo a ordem de inserção original.

## TESTES ADICIONADOS
Foram adicionados cenários cobrindo:
- Clientes VIP abaixo e acima de R$ 1.000,00;
- Desconto de funcionários (`employee`) e clientes regulares (`regular`);
- Trava do teto máximo de 25% de desconto cumulativo;
- Aplicação restrita do cupom `VIP50` apenas para clientes VIP;
- Cobrança de frete expresso em compras acima de R$ 500,00 fora do Sudeste;
- Alíquota de imposto padrão (12%) para estados fora do eixo MG/SP/RJ/ES;
- Filtro de itens com quantidade zero no subtotal e detecção de múltiplos itens duplicados.

## MÉTRICAS ANTES E DEPOIS
Consulte o arquivo [METRICS.md](./METRICS.md) para a tabela comparativa detalhada.

## DECISÕES TÉCNICAS
- **Preservação de Interface e Efeitos Colaterais:** Mantivemos a assinatura de `process_order`, o registro na lista global `ORDERS_PROCESSED` e a saída no console (`print`) para garantir total retrocompatibilidade com testes externos.
- **Cálculo de Pontos Antes do Arredondamento:** No código original, os pontos eram calculados sobre `valor_com_desconto + frete + imposto` antes do `round(..., 2)`. Mantivemos essa exata ordem matemática (`raw_total`) para evitar divergências de arredondamento em casos limite.

## USO DE INTELIGÊNCIA ARTIFICIAL
- **Ferramenta utilizada:** Gemini (Google).
- **Finalidade:** Diagnóstico de erro de configuração do `PYTHONPATH` no Pytest, sugestões de extração de funções e estruturação de casos de teste.
- **Exemplo de sugestão recebida:** Substituição do loop aninhado de busca de duplicados por `collections.Counter` e separação do cálculo de descontos em subfunções.
- **A sugestão foi aceita, modificada ou rejeitada?** Aceita com adaptações para extrair todas as constantes de negócio (Magic Numbers) exigidas nos critérios da disciplina.
- **Como a equipe validou a solução?** Executando a suíte de testes automatizados (`pytest`), verificando 100% de cobertura (`pytest-cov`) e validando a queda de complexidade ciclomática no `radon` e ausência de alertas no `ruff`.

## MELHORIAS FUTURAS
- **Remoção do estado global (`ORDERS_PROCESSED`):** Em uma evolução arquitetural, a persistência de pedidos deveria ser injetada via repositório ou banco de dados, eliminando variáveis globais mutáveis.
- **Validação de entrada com tipos estruturados:** Utilizar `dataclasses` ou `Pydantic` para representar `Customer` e `OrderItem`, impedindo quantidades ou preços negativos na criação do objeto.
- **Substituição de `print` por `logging`:** Desacoplar a exibição no terminal utilizando o módulo padrão `logging`.