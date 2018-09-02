from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask import request
import pymysql
app = Flask(__name__)
bootstrap = Bootstrap(app)
from flask import send_file

@app.route('/')
def index():
    return render_template('index.html')

def getConnection():
    conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', db='paindatabase', charset='utf8')
    return conn

@app.route('/drug')
def drug():
    conn=getConnection()
    cur = conn.cursor()
    sql_kegg_drug_drugbank = "SELECT drugbank_id FROM drugbank_keggdrug"
    cur.execute(sql_kegg_drug_drugbank)
    drugbank_id_list = cur.fetchall()
    #print("drugbank_id_list",drugbank_id_list)
    drugbank_cur=conn.cursor()
    drug_info_list=[]
    for drugbank_id in drugbank_id_list:
        if len(drugbank_id)>0:
            drugbank_id=list(drugbank_id)[0]
            sql_drugbank="SELECT drugbank_id,drugbank_Name,Description FROM drugbank WHERE drugbank_id = '%s'" %drugbank_id
            drugbank_cur.execute(sql_drugbank)
            item=drugbank_cur.fetchone()
            drug_info_list.append(item)
    drugbank_cur.close()
    cur.close()
    conn.close()
    #print("drug_info_list:",drug_info_list)
    return render_template('drug.html',drug_info_list=drug_info_list)

@app.route('/drugInfo',methods=["get"])
def drugInfo():
    req=request.args
    drugbank_id=req.get("drugbank_id")
    #drugbank_id=drugbank_id
    print("drugbank_id:",drugbank_id)
    conn=getConnection()
    cur = conn.cursor()
    sql_drug = "SELECT * FROM drugbank WHERE drugbank_id = '%s'" %drugbank_id
    cur.execute(sql_drug)
    drugbank_info_tuple=cur.fetchone()
    print("drugbank_info_tuple:",drugbank_info_tuple)
    #drugbank_kegg联系表 获取kegg_id
    # cur2 = conn.cursor()
    # sql_kegg_drugbank = 'SELECT * FROM drugbank_keggdrug WHERE drugbank_id = "%s"' %drugbank_id
    # cur2.execute(sql_kegg_drugbank)
    # kegg_drugbank_info_tuple=cur2.fetchone()
    # print("kegg_drugbank_info_tuple:",kegg_drugbank_info_tuple)
    kegg_id=drugbank_info_tuple[10]
    print("kegg_id:",kegg_id)
    #根据keggid获取kegg表数据
    cur3 = conn.cursor()
    sql_kegg_drug = "SELECT * FROM kegg_drug WHERE kegg_id = '%s'" %kegg_id
    cur3.execute(sql_kegg_drug)
    kegg_drug_info_tuple=cur3.fetchone()
    print("kegg_drug_info_tuple:",kegg_drug_info_tuple)
    if kegg_drug_info_tuple==None:
        kegg_drug_info_tuple=[]
        for item_i in range(21):
            kegg_drug_info_tuple.append("None")
    #查询pathway
    cur_pathway=conn.cursor()
    sql_pathway="SELECT * FROM pathway_table WHERE drugbank_id = '%s'" %drugbank_id
    cur_pathway.execute(sql_pathway)
    pathways=cur_pathway.fetchall()
    print("pathways:",pathways)
    #查询drugbank target
    cur_target=conn.cursor()
    sql_target="SELECT * FROM drugbank_target WHERE drugbank_id = '%s'" %drugbank_id
    cur_target.execute(sql_target)
    drugbank_target=cur_target.fetchall()
    print("drugbank_target:",drugbank_target)
    print("img.........................:",kegg_drug_info_tuple[4])
    print("structureMapName:",kegg_drug_info_tuple[12])
    return render_template('drugInfo.html',drugbank_info_tuple=drugbank_info_tuple
        ,kegg_drug_info_tuple=kegg_drug_info_tuple,pathways=pathways,drugbank_target=drugbank_target)

@app.route('/sideeffects')
def sideeffects():
    conn=getConnection()
    cur = conn.cursor()
    sql_sideeffect = "SELECT * FROM sider_effect WHERE sideeffect_link IN (SELECT sideeffect_link FROM sideeffect_of_sider_drug WHERE sider_drug_link IN (SELECT sider_drug_link FROM siderdrug_drugbank WHERE drugbank_id IN (SELECT drugbank_id FROM drugbank_keggdrug )));"
    cur.execute(sql_sideeffect)
    sideeffect_names=cur.fetchall()
    sideeffect_names=list(sideeffect_names)
    #print("sideeffect_names:",sideeffect_names)
    len_sider=len(sideeffect_names)
    item3_len=int(len_sider/3)
    print(item3_len)
    return render_template('sideeffects.html',sideeffect_names=sideeffect_names,item3_len=item3_len)

@app.route('/sideInfo',methods=["get"])
def sideInfo():
    req=request.args
    sideName=req.get("sideName")
    #drugbank_id=drugbank_id
    print("sideName:",sideName)
    conn=getConnection()
    cur = conn.cursor()
    sqlSideInfo = 'SELECT * FROM sider_effect WHERE sideeffect_name = "%s"' %sideName
    cur.execute(sqlSideInfo)
    SideInfo=cur.fetchone()
    #SideInfo=list(SideInfo)
    print("SideInfo:",SideInfo)
    print("SideInfo[0]:",SideInfo[0])
    #根据sidereffect_link 查 对应的多种副作用药物
    cur_drug=conn.cursor()
    sql_drug="SELECT * FROM sider_to_drug WHERE sideeffect_link='%s'" %SideInfo[0]
    cur_drug.execute(sql_drug)
    drugOFsider=cur_drug.fetchall()
    print("drugOFsider:",drugOFsider)
    return render_template('sideInfo.html',SideInfo=SideInfo,drugOFsider=drugOFsider)

@app.route('/structureMap',methods=["get"])
def structureMap():
    req=request.args
    structureMapName=req.get("structureMapName")
    print("structureMapName:",structureMapName)
    conn=getConnection()
    cur = conn.cursor()
    sqlmap = 'SELECT * FROM kegg_drug WHERE Structure_map_name = "%s"' %structureMapName
    cur.execute(sqlmap)
    kegg_drug=cur.fetchone()
    print("kegg_drug_info:",kegg_drug)
    return render_template('structureMap.html',kegg_drug=kegg_drug)

@app.route('/keggTarget',methods=["get"])
def keggTarget():
    req=request.args
    Target_href=req.get("Target_href")
    print("Target_href:",Target_href)
    targetInfo=[]
    conn=getConnection()
    if Target_href=="None" or Target_href==None:
        for i in range(20):
            targetInfo.append("None")
    else:
        cur = conn.cursor()
        sql_target = 'SELECT * FROM kegg_drug_target WHERE Target_href = "%s"' %Target_href
        cur.execute(sql_target)
        targetInfo=cur.fetchone()
    print("targetInfo:",targetInfo)
    pathwayList=[]
    if Target_href==None or Target_href=="None":
        for i in range(20):
            pathwayList.append("None")
    else:
        cur2 = conn.cursor()
        sql_pathway = 'SELECT * FROM target_pathway WHERE Target_href = "%s"' %Target_href
        cur2.execute(sql_pathway)
        pathwayList=cur2.fetchall()

    return render_template('targetInfo.html',targetInfo=targetInfo,pathwayList=pathwayList)

@app.route('/pathwayInfo',methods=["get"])
def pathwayInfo():
    req=request.args
    pathwayHsa=req.get("pathwayHsa")
    print("pathwayHsa:",pathwayHsa)
    conn=getConnection()
    pathwayHsaInfo=[]
    if pathwayHsa!=None and pathwayHsa!="None":
        cur = conn.cursor()
        sql_target = 'SELECT * FROM target_pathway WHERE kegg_target_hsa = "%s"' %pathwayHsa
        cur.execute(sql_target)
        pathwayHsaInfo=cur.fetchone()
    return render_template('pathwayHsaInfo.html',pathwayHsaInfo=pathwayHsaInfo)

@app.route('/pathway')
def pathway():
    conn=getConnection()
    cur = conn.cursor()
    sql_target = 'SELECT * FROM target_pathway'
    cur.execute(sql_target)
    pathwayHsaList=cur.fetchall()
    return render_template('pathwayHsaList.html',pathwayHsaList=pathwayHsaList)
    
if __name__ == '__main__':
    #getDrugList()
    app.run(port=5009)
