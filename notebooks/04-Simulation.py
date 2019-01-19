#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents &lt;br&gt;&lt;/br&gt;<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><ul class="toc-item"><li><span><a href="#Imports-and-Data-loading" data-toc-modified-id="Imports-and-Data-loading-0.1"><span class="toc-item-num">0.1&nbsp;&nbsp;</span>Imports and Data loading</a></span><ul class="toc-item"><li><span><a href="#4.6kW-Chargers" data-toc-modified-id="4.6kW-Chargers-0.1.1"><span class="toc-item-num">0.1.1&nbsp;&nbsp;</span>4.6kW Chargers</a></span></li><li><span><a href="#3.6kW-Chargers" data-toc-modified-id="3.6kW-Chargers-0.1.2"><span class="toc-item-num">0.1.2&nbsp;&nbsp;</span>3.6kW Chargers</a></span></li></ul></li></ul></li><li><span><a href="#Real-data-comparison" data-toc-modified-id="Real-data-comparison-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Real data comparison</a></span><ul class="toc-item"><li><ul class="toc-item"><li><span><a href="#4.6kw-chargers-(only-time-on-chargers-simulated)" data-toc-modified-id="4.6kw-chargers-(only-time-on-chargers-simulated)-1.0.1"><span class="toc-item-num">1.0.1&nbsp;&nbsp;</span>4.6kw chargers (only time on chargers simulated)</a></span></li></ul></li><li><span><a href="#Plot-differences" data-toc-modified-id="Plot-differences-1.1"><span class="toc-item-num">1.1&nbsp;&nbsp;</span>Plot differences</a></span></li></ul></li><li><span><a href="#Demand-Patterns" data-toc-modified-id="Demand-Patterns-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Demand Patterns</a></span><ul class="toc-item"><li><span><a href="#Yearly-rental-patterns" data-toc-modified-id="Yearly-rental-patterns-2.1"><span class="toc-item-num">2.1&nbsp;&nbsp;</span>Yearly rental patterns</a></span></li><li><span><a href="#Weekly-Pattern-of-connected-EVS" data-toc-modified-id="Weekly-Pattern-of-connected-EVS-2.2"><span class="toc-item-num">2.2&nbsp;&nbsp;</span>Weekly Pattern of connected EVS</a></span></li><li><span><a href="#Daily-Pattern-of-connected-EVS" data-toc-modified-id="Daily-Pattern-of-connected-EVS-2.3"><span class="toc-item-num">2.3&nbsp;&nbsp;</span>Daily Pattern of connected EVS</a></span></li><li><span><a href="#2.4.-Average-Daily-Pattern" data-toc-modified-id="2.4.-Average-Daily-Pattern-2.4"><span class="toc-item-num">2.4&nbsp;&nbsp;</span>2.4. Average Daily Pattern</a></span></li></ul></li></ul></div>

# ## Imports and Data loading

# In[1]:


# Display plots inline
get_ipython().run_line_magic('matplotlib', 'inline')

# Autoreload all package before excecuting a call
get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# In[2]:


from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from evsim.data import load_car2go_trips, load_car2go_capacity


# ### 4.6kW Chargers

# In[3]:


df_4 = pd.read_csv("../logs/stats-Tobi-4-6.csv", parse_dates=[0], infer_datetime_format=True)
df_4 = df_4.set_index("timestamp")
df_4.describe()


# ### 3.6kW Chargers

# In[4]:


df_3 = pd.read_csv("../logs/stats-3_6-big.csv", parse_dates=[0], infer_datetime_format=True)
df_3 = df_3.set_index("timestamp")
df_3.describe()


# # Real data comparison

# In[5]:


real_cap = load_car2go_capacity()


# ### 4.6kw chargers (only time on chargers simulated)

# In[6]:


real_cap.describe()


# ## Plot differences

# In[7]:


merge = df_3.merge(real_cap, left_index=True, right_index=True, how='left')
merge["fleet_soc_diff"] = merge["fleet_soc_x"] - merge["fleet_soc_y"]
print("Average SoC difference: %.2f" % merge.fleet_soc_diff.mean())

merge = merge.rolling(window=int(1 * 12 * 24)).mean()
ax = merge.plot(y='fleet_soc_x', label='Fleet SoC Simulation')
merge.plot(y='fleet_soc_y', label='Fleet SoC Real', ax=ax)
plt.show()


# In[8]:


merge[["fleet_soc_x", "fleet_soc_y"]].head(20)


# # Demand Patterns

# In[9]:


def apply_smoother(df, days):
    DAY = 12*24

    df['vpp_avg'] = df['ev_vpp'].rolling(
        window=int(days*DAY)).mean()
    df['vpp_soc_avg'] = df['vpp_soc'].rolling(
        window=int(days*DAY)).mean()
    df['vpp_capacity_kw_avg'] = df['vpp_capacity_kw'].rolling(
        window=int(days*DAY)).mean()

    return df


def plot(df, title, start="2016-12-1", end="2017-04-28"):
    X = df.loc[start:end][['vpp_avg', 'vpp_soc_avg', 'vpp_capacity_kw_avg']]
    return X.plot(figsize=(12, 4), title=title)


# ## Yearly rental patterns

# In[10]:


df = apply_smoother(df_3, days=14)
plot(df, "Yearly rental patterns")


# ## Weekly Pattern of connected EVS

# In[11]:


df = apply_smoother(df_3, days=0.5)
plot(df, "Weekly rental patterns", start=datetime(
    2017, 1, 1), end=datetime(2017, 1, 7))


# ## Daily Pattern of connected EVS

# In[12]:


df = apply_smoother(df_3, days=1/24)
plot(df, "Daily rental patterns", start=datetime(
    2017, 1, 5), end=datetime(2017, 1, 6))


# ## 2.4. Average Daily Pattern

# In[13]:


df["hour"] = df.index.hour

f, (ax1, ax2) = plt.subplots(1, 2)
f.set_size_inches(18.5, 10.5)
sns.violinplot(x="hour", y="fleet_soc", data=df, ax=ax1)
sns.violinplot(x="hour", y="ev_vpp", data=df, ax=ax2)

