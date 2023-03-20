import cartolafc

api = cartolafc.Api(attempts=5)

print(api.clubes())
print(api.ligas(query="Virtus"))
print(api.ligas_patrocinadores())
print(api.mercado())
print(api.mercado_atletas())
print(api.parciais())
print(api.partidas(1))
print(api.pos_rodada_destaques())
print(api.time(id=2706236))
print(api.time(nome="ALCAFLA FC"))
print(api.time(slug="alcafla-fc"))
print(api.time_parcial(id=2706236))
print(api.time_parcial(nome="ALCAFLA FC"))
print(api.time_parcial(slug="alcafla-fc"))
print(api.times(query="Faly"))
