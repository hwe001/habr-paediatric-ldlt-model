import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=[  # label, lo, hi, color-group
 ('Postoperative calibre growth (0-20% each vessel)', -44.3, 128.8, 'c'),
 ('HABR coefficients (x0.5 to x1.5)', 12.8, 37.9, 'h'),
 ('POD 1 identifiability family (P_HA,amp 24-60 mmHg)', 20.2, 27.1, 'p'),
 ('Hepatic-artery baseline diameter (1.0-1.4 mm)', 23.7, 26.4, 'p'),
 ('Mean arterial pressure P_HA,mean (43-65 mmHg)', 22.5, 27.0, 'p'),
 ('Inferior vena cava pressure (0-5 mmHg)', 24.7, 25.8, 'p'),
 ('Graft-mass scaling of portal flow (x0.5-2)', 25.1, 25.5, 'p'),
 ('HR, C_sinus, C_hv, R_p,sinus, L_HV, R_s,HV, R_p,hv,out', 25.3, 25.3, 'p'),
]
col={'c':'#c0392b','h':'#1f5fa8','p':'#7f8c8d'}
fig,ax=plt.subplots(figsize=(8.2,3.6),dpi=200)
for i,(lab,lo,hi,g) in enumerate(rows[::-1]):
    ax.barh(i,max(hi-lo,0.6),left=lo if hi>lo else lo-0.3,color=col[g],height=0.55)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]],fontsize=7)
ax.axvline(25.3,color='k',ls=':',lw=1); ax.axvline(0,color='k',lw=0.6); ax.axvline(100,color='gray',ls='--',lw=0.8)
ax.text(101,len(rows)-0.6,'measured decline',fontsize=6.5,color='gray')
ax.set_xlabel('Fraction of measured PSV decline reproduced at POD 30, F (%)',fontsize=8)
for s in ('top','right'): ax.spines[s].set_visible(False)
ax.tick_params(axis='x',labelsize=7)
plt.tight_layout(); plt.savefig('fig9.png')
