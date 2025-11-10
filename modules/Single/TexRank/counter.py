text = """There is a definite lull in "earnings season." Most major companies will report second quarter results in mid-July. But some notable companies, including two Dow components, are on tap to release results this week. \n \n Nike (NKE) will report its earnings after the closing bell Monday. Shares of the sneaker and athletic apparel giant are down nearly 35% this year. \n \n Tampon shortage: Instacart says it&#39;s struggling to fulfill orders \n \n Tampon shortage: Instacart says it\'s struggling to fulfill orders \n \n The company reported solid results in March, but geopolitical worries have weighed on Nike\'s stock. Analysts are predicting that Nike will post a decline in sales and earnings per share for the quarter. Nike also just announced it\'s exiting Russia in light of the invasion of Ukraine. \n \n Walgreens (WBA) will also report results before the market opens on Thursday. Shares are down 20% this year, double the 10% drop for rival CVS (CVS) but not as bad as the nearly 45% plunge for Rite Aid (RAD). \n \n It\'s been a challenging second year for Walgreens CEO Rosalind Brewer, who took the top job in March 2021. \n \n The veteran executive, who had previous leadership roles at Walmart (WMT) and Starbucks (SBUX), is dealing with supply chain disruptions and concerns about a slowdown in the economy and weakening consumer demand — a problem facing all retailers. Wall Street is predicting that revenue and net income will fall from a year ago. ||||  But EA has been acquisitive in its own right and could be looking for further deals, particularly ones that could bolster its mobile gaming division. EA made two such acquisitions in 2021, Glu for $2.4 billion and Playdemic (formerly owned by previous CNN parent AT&T (T)) for $1.4 billion. \n \n Analysts at Goldman Sachs estimate that there\'s about a 15% probability that EA could itself be acquired, "given heightened levels of M&A activity within the video game space," according to a recent report about the broader tech sector. It\'s a small chance to be sure, but it\'s bigger than zero. \n \n The analysts came up with a potential takeover valuation of $190 a share, which is "consistent with recent video game transactions." That\'s nearly 50% above EA\'s current stock price. \n \n Still, EA has enough quality content to justify going it alone for the foreseeable future. \n \n Wells Fargo analyst Brian Fitzgerald noted in a report after EA\'s latest earnings came out in May that a "solid pipeline" (more games from EA Sports, plus updates to The Sims, Lord of the Rings and Bioware franchises) as well as "accelerating mobile growth" were positives for the stock. \n \n So EA may not need to sell itself to a larger company to remain competitive in the video game world. |||| """
texs1 = text.split("||||")
texs2 = [t.split("\n \n") for t in texs1]
texs3 = []
le = 0
for t in texs2:
    for t1 in t:
        texs3.append(t1)
texs4 = [t.split(". ") for t in texs3]
texs5 = []
for t in texs4:
    for t1 in t:
        if (t1 != ''):
            texs5.append(t1)
print(len(texs5))
def post_proc(summary):

    summary = summary.replace('\"', '"')
    summary = summary.replace("\'", "'")
    summary = summary.replace("\"", '"')
    summary = summary.replace("\\n", '')
    summary = summary.replace("\\", '')
    summary = summary.replace("||||", '')
    summary = summary.replace("  ", ' ')
    summary = summary.strip()
    summary = summary[0].upper() + summary[1:]
    return summary

def count_sentences(document, per):
    texs1 = document.split("||||")
    texs2 = [t.split("\n \n") for t in texs1]
    texs3 = []
    le = 0
    for t in texs2:
        for t1 in t:
            texs3.append(t1)
    texs4 = [t.split(". ") for t in texs3]
    texs5 = []
    for t in texs4:
        for t1 in t:
            if (t1 != '' and t1 != ' '):
                texs5.append(t1)
    x = len(texs5)
    print(round(x * per))
    if(round(x* per) <2):
        return 2
    else:
        return round(x* per)

def short_count_sentences(document, percent_output):
    texs1 = document.split("||||")
    texs2 = [t.split("\n") for t in texs1]
    texs3 = []
    le = 0
    for t in texs2:
        for t1 in t:
            texs3.append(t1)
    texs4 = [t.split(". ") for t in texs3]
    texs5 = []
    for t in texs4:
        for t1 in t:
            if (t1 != ''):
                texs5.append(t1)
    x = len(texs5) 
    percent =  round(x * percent_output)
    decimal = percent / 1
    if decimal <0.5:
        percent +=1
    if percent ==0:
        percent +=1
    return percent

def normal_count_sentences(document, percent_output):
    texs1 = document.split("\n")
    texs2 = [t.split("\n") for t in texs1]
    texs3 = []
    le = 0
    for t in texs2:
        for t1 in t:
            texs3.append(t1)
    texs4 = [t.split(". ") for t in texs3]
    texs5 = []
    for t in texs4:
        for t1 in t:
            if (t1 != ''):
                texs5.append(t1)
    x = len(texs5)
    return round(x * percent_output)+1

def sortByDocToArr(para, sens):
    paras = para
    result = [[] for i in range(len(paras))]
    for sen in sens:
        for idx, para in enumerate(paras):
            if (sen in para):
                result[idx].append(sen)
                break
    return result

def sortByDocToStr(para, sens):
    result = ""
    docs = sortByDocToArr(para, sens)
    # for d in docs:
    #     print(d)
    for d in docs:
        for s in d:
            result += "\n\u2022\r"
            result += s
            #result += post_proc(s)
        result += "\n"
    
    return result
        

