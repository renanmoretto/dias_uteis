# dias_uteis
Biblioteca feita para facilitar o uso e cálculos de dias úteis no calendário brasileiro.

- Sem dependências externas. Nada além do puro Python é utilizado.
- Testado em todas versões do Python desde a 3.6.
- Fácil uso, API simples.
- Extrememente leve.

# Instalação
```
pip install dias_uteis
```

# Uso
```python
import datetime
import dias_uteis as dus
```
```
>>> dus.last_du()
datetime.date(2023, 11, 7)

>>> dus.next_du() 
datetime.date(2023, 11, 9)

>>> date = datetime.date(2023,11,8)
>>> dus.is_du(date)
True

>>> dus.delta_du(date, 5) 
datetime.date(2023, 11, 16) # 5 dias úteis após o dia 8/11/2023 é 16/11/2023

>>> dus.delta_du(date, -2) 
datetime.date(2023, 11, 6) # 2 dias úteis antes do dia 8/11/2023 é 6/11/2023

>>> dus.diff_du(datetime.date(2023,11,6), datetime.date(2023,11,16))
7

>>> start = datetime.date(2023,10,20) 
>>> end = datetime.date(2023,11,7)  
>>> dus.du_range(start, end)
[datetime.date(2023, 10, 20), datetime.date(2023, 10, 23), datetime.date(2023, 10, 24),
datetime.date(2023, 10, 25), datetime.date(2023, 10, 26), datetime.date(2023, 10, 27),
datetime.date(2023, 10, 30), datetime.date(2023, 10, 31), datetime.date(2023, 11, 1), 
datetime.date(2023, 11, 3), datetime.date(2023, 11, 6)]
```

# Contribuições
Contribuições/sugestões são bem-vindas. Por favor, abra um issue ou envie um pull request para melhorias.