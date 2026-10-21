"""Save the dashboard charts as HTML and PNG files."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import dashboard

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
all_sites=dashboard.get_pie_chart('ALL')
site_labels=list(all_sites.data[0].labels);site_values=list(all_sites.data[0].values)
assert sum(site_values)==24
fig,ax=plt.subplots(figsize=(10,6))
ax.pie(site_values,labels=[f'{label}: {value}' for label,value in zip(site_labels,site_values)],
       autopct='%1.1f%%',startangle=90,textprops={'fontsize':12},
       wedgeprops={'edgecolor':'white'})
ax.set_title('Successful landings by launch site',fontsize=17)
fig.text(.5,.02,'24 positive outcomes in the IBM dashboard dataset (56 records).',ha='center',fontsize=11)
fig.tight_layout(rect=(0,.04,1,1));fig.savefig(OUT/'dashboard_successes_by_site.png',dpi=160);plt.close(fig)
pie=dashboard.get_pie_chart('KSC LC-39A')
pie.write_html(OUT/'dashboard_ksc_pie.plotly.html',include_plotlyjs='cdn',full_html=True)
labels=list(pie.data[0].labels);values=list(pie.data[0].values)
assert dict(zip(labels,values))=={'Failure':3,'Success':10}
fig,ax=plt.subplots(figsize=(9,5.2))
ax.pie(values,labels=[f'{label}: {value}' for label,value in zip(labels,values)],
       colors=['#c44747','#247a68'],autopct='%1.1f%%',startangle=90,
       textprops={'fontsize':14},wedgeprops={'edgecolor':'white'})
ax.set_title('KSC LC-39A: 10 positive outcomes in 13 records',fontsize=16)
fig.text(.5,.02,'IBM dashboard dataset: 13 launch records at KSC LC-39A.',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.04,1,1));fig.savefig(OUT/'dashboard_ksc_pie.png',dpi=160);plt.close(fig)

scatter=dashboard.get_scatter_chart('KSC LC-39A',[3000,9600])
scatter.write_html(OUT/'dashboard_ksc_payload.plotly.html',include_plotlyjs='cdn',full_html=True)
fig,ax=plt.subplots(figsize=(10,5.2))
count=0
for trace in scatter.data:
    xs=list(trace.x);ys=list(trace.y);count+=len(xs)
    assert all(3000<=float(x)<=9600 for x in xs)
    ax.scatter(xs,ys,label=trace.name,color=trace.marker.color,s=70,alpha=.8)
assert count==11
ax.set(xlabel='Payload mass (kg)',ylabel='Dataset class',ylim=(-.2,1.2),xlim=(3000,9600))
ax.set_yticks([0,1],['0','1']);ax.legend(title='Booster category',loc='upper right')
ax.set_title('KSC LC-39A: 11 records with payload 3,000-9,600 kg',fontsize=16)
ax.grid(axis='x',alpha=.18)
fig.text(.5,.01,'IBM dashboard dataset. B5 has one record in this view.',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.04,1,1));fig.savefig(OUT/'dashboard_ksc_payload.png',dpi=160);plt.close(fig)
print('Saved three PNG charts and two interactive HTML charts')
