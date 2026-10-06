C={'F1':(882,1074),'F3':(1082,1274),'RD':(1550,1744),'RE':(1752,1948)}  # x interior das colunas
HL=[702,751,799,847,895,943,991,1038,1086,1134,1181,1222]               # linhas horizontais (lado Fixo)
HR=[695,744,793,841,889,938,985,1033,1081,1129,1177,1217]               # linhas horizontais (lado Rotor)
def cell(c,r,t):
    hl=HL if c in('F1','F3') else HR
    return (C[c][0],hl[r-1]+4,C[c][1],hl[r]-4,t)
F=[cell('F1',1,'862.6'), cell('F1',4,'13.2/13.9'), (1553,1918,1815,1958,'',{'erase_only':1}),
   (440,2300,740,2390,'Juliano',{'sig':1})]
