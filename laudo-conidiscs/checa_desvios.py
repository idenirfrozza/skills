# S[p]['L'|'R'][linha] = (nominal ou (n1,n2), desvio_inf, desvio_sup)
def fora(texto, nom, mi, pl):
    vals=[float(v) for v in texto.replace(',','.').split('/')]
    noms=nom if isinstance(nom,tuple) else (nom,)*len(vals)
    return [v for v,n in zip(vals,noms) if not (n-mi-1e-9 <= v <= n+pl+1e-9)]
