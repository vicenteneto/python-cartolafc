import cartolafc

api = cartolafc.Api(attempts=5)

print(api.clubes())
print(api.ligas(query="Teste"))
print(api.ligas_patrocinadores())
print(api.mercado())
print(api.mercado_atletas())
print(api.parciais())
print(api.partidas(1))
print(api.pos_rodada_destaques())
print(api.time(time_id=471815))
print(api.time_parcial(time_id=471815))
print(api.times(query='Falydos FC'))
