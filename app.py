from flask import Flask
from flask import render_template
from flask import redirect, url_for
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

@app.route('/drugInfo',methods=["get","post"])
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
    ####
    cur_sideefect=conn.cursor()
    sql_sideeffects='SELECT * FROM sider_effect WHERE sideeffect_link IN (SELECT sideeffect_link FROM sideeffect_of_sider_drug WHERE sider_drug_link IN (SELECT sider_drug_link FROM siderdrug_drugbank WHERE drugbank_id = "%s" ))'%drugbank_id
    cur_sideefect.execute(sql_sideeffects)
    sideeffects=cur_sideefect.fetchall()
    #####
    # cur_kegg_pathway=conn.cursor()
    # sql_kegg_pathway=''
    print("sideeffects:",sideeffects)
    print("drugbank_target:",drugbank_target)
    print("img.........................:",kegg_drug_info_tuple[4])
    print("structureMapName:",kegg_drug_info_tuple[12])
    return render_template('drugInfo.html',drugbank_info_tuple=drugbank_info_tuple
        ,kegg_drug_info_tuple=kegg_drug_info_tuple,pathways=pathways,
        drugbank_target=drugbank_target,sideeffects=sideeffects)

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
    diseaseList = []
    if Target_href==None or Target_href=="None":
        for i in range(10):
            diseaseList=None
    else:
        cur_disease = conn.cursor()
        sql = 'SELECT * FROM target_disease WHERE Target_href = "%s"' %Target_href
        cur_disease.execute(sql)
        diseaseList=cur_disease.fetchall()
    print("diseaseList:",diseaseList)
    return render_template('targetInfo.html',targetInfo=targetInfo,pathwayList=pathwayList,diseaseList=diseaseList)

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

@app.route('/pathwayMapOfKegg',methods=["get"])
def pathwayMapOfKegg():
    req=request.args
    picName=req.get("picName")
    print("picName:",picName)
    return render_template('pathwayMapOfKegg.html',picName=picName)

@app.route('/targets')
def targets():
    conn=getConnection()
    cur = conn.cursor()
    sql_target = 'SELECT * FROM drugbank_target'
    cur.execute(sql_target)
    drugbankTargetList=cur.fetchall()
    len_list=len(drugbankTargetList)
    item_len=(int)(len_list/2)
    return render_template('drugbankTarget.html',drugbankTargetList=drugbankTargetList,item_len=item_len)

@app.route('/drugbankTargetInfo',methods=["get"])
def drugbankTargetInfo():
    req=request.args
    drugbankTarget=req.get("drugbankTarget")
    print("drugbankTarget:",drugbankTarget)
    conn=getConnection()
    cur = conn.cursor()
    sql_target = 'SELECT * FROM drugbank_target WHERE target_name = "%s"' %drugbankTarget
    cur.execute(sql_target)
    drugbankTargetInfo=cur.fetchone()
    return render_template('drugbankTargetInfo.html',drugbankTargetInfo=drugbankTargetInfo)
@app.route('/Disease')
def Disease():
    conn=getConnection()
    cur = conn.cursor()
    sql = 'SELECT * FROM kegg_disease'
    cur.execute(sql)
    diseaseList=cur.fetchall()
    return render_template('diseases.html',diseaseList=diseaseList)
@app.route('/diseaseInfo',methods=["get"])

@app.route('/diseaseInfo',methods=["get"])
def diseaseInfo():
    req=request.args
    keggDiseaseId=req.get("keggDiseaseId")
    print("keggDiseaseId:",keggDiseaseId)
    conn=getConnection()
    cur = conn.cursor()
    sql = 'SELECT * FROM kegg_disease WHERE kegg_disease_id = "%s"' %keggDiseaseId
    cur.execute(sql)
    diseaseInfo=cur.fetchone()

    #查基因信息
    cur_genen=conn.cursor()
    sql_gene='SELECT * FROM kegg_disease_gene WHERE kegg_id = "%s"' %keggDiseaseId
    cur_genen.execute(sql_gene)
    geneInfoList=cur_genen.fetchall()
    return render_template('diseaseInfo.html',diseaseInfo=diseaseInfo,geneInfoList=geneInfoList)

@app.route('/diseasePathway',methods=["get"])
def diseasePathway():
    req=request.args
    diseasePathway=req.get("diseasePathway")
    print("diseasePathway:",diseasePathway)
    conn=getConnection()
    cur = conn.cursor()
    sql = 'SELECT * FROM kegg_disease WHERE kegg_disease_pathway_id = "%s"' %diseasePathway
    cur.execute(sql)
    diseasePathwayInfo=cur.fetchone()
    return render_template('diseasePathwayInfo.html',diseasePathwayInfo=diseasePathwayInfo)

@app.route('/pai')
def pai():
    return render_template('pai.html')

#@app.route('/PainDatabase/drugbankInfomation?drugbank_id=<drugbank_id>')
def drugbankInfomation(drugbank_id):
    #drugbank_id=drugbank_id
    print("drugbank_id:",drugbank_id)
    conn=getConnection()
    cur = conn.cursor()
    sql_drug = "SELECT * FROM drugbank WHERE drugbank_id = '%s'" %drugbank_id
    cur.execute(sql_drug)
    drugbank_info_tuple=cur.fetchone()
    print("drugbank_info_tuple:",drugbank_info_tuple)
 
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
    ####
    cur_sideefect=conn.cursor()
    sql_sideeffects='SELECT * FROM sider_effect WHERE sideeffect_link IN (SELECT sideeffect_link FROM sideeffect_of_sider_drug WHERE sider_drug_link IN (SELECT sider_drug_link FROM siderdrug_drugbank WHERE drugbank_id = "%s" ))'%drugbank_id
    cur_sideefect.execute(sql_sideeffects)
    sideeffects=cur_sideefect.fetchall()
    #####
    # cur_kegg_pathway=conn.cursor()
    # sql_kegg_pathway=''
    print("sideeffects:",sideeffects)
    print("drugbank_target:",drugbank_target)
    print("img.........................:",kegg_drug_info_tuple[4])
    print("structureMapName:",kegg_drug_info_tuple[12])
    return render_template('drugInfo.html',drugbank_info_tuple=drugbank_info_tuple
        ,kegg_drug_info_tuple=kegg_drug_info_tuple,pathways=pathways,
        drugbank_target=drugbank_target,sideeffects=sideeffects)

@app.route('/searchForSideName?sideName=<sideName>')
def searchForSideName(sideName):
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

@app.route('/searchForTargetName?target_name=<target_name>')
def searchForTargetName(target_name):
    drugbankTarget=target_name
    print("drugbankTarget:",drugbankTarget)
    conn=getConnection()
    cur = conn.cursor()
    sql_target = 'SELECT * FROM drugbank_target WHERE target_name = "%s"' %drugbankTarget
    cur.execute(sql_target)
    drugbankTargetInfo=cur.fetchone()
    return render_template('drugbankTargetInfo.html',drugbankTargetInfo=drugbankTargetInfo)

@app.route('/searchForKeggPathway?pathwayHsa=<pathwayHsa>')   
def searchForKeggPathway(pathwayHsa):
    print("pathwayHsa:",pathwayHsa)
    conn=getConnection()
    pathwayHsaInfo=[]
    if pathwayHsa!=None and pathwayHsa!="None":
        cur = conn.cursor()
        sql_target = 'SELECT * FROM target_pathway WHERE kegg_target_hsa = "%s"' %pathwayHsa
        cur.execute(sql_target)
        pathwayHsaInfo=cur.fetchone()
    return render_template('pathwayHsaInfo.html',pathwayHsaInfo=pathwayHsaInfo)

@app.route('/searchForKeggDiseaseId?keggDiseaseId=<keggDiseaseId>')
def searchForKeggDiseaseId(keggDiseaseId):
    print("keggDiseaseId:",keggDiseaseId)
    conn=getConnection()
    cur = conn.cursor()
    sql = 'SELECT * FROM kegg_disease WHERE kegg_disease_id = "%s"' %keggDiseaseId
    cur.execute(sql)
    diseaseInfo=cur.fetchone()

    #查基因信息
    cur_genen=conn.cursor()
    sql_gene='SELECT * FROM kegg_disease_gene WHERE kegg_id = "%s"' %keggDiseaseId
    cur_genen.execute(sql_gene)
    geneInfoList=cur_genen.fetchall()
    return render_template('diseaseInfo.html',diseaseInfo=diseaseInfo,geneInfoList=geneInfoList)

@app.route('/search',methods=["post","get"])
def search():
    username=request.form.get("username")
    print("username:",username)
    conn = getConnection()
    #drugbank_id查drugbank
    cur_drugbank = conn.cursor()
    args='%'+username+'%'
    sql_drugbank="select * from drugbank where drugbank_id LIKE '%s'" %args
    cur_drugbank.execute(sql_drugbank)
    drugbankInfo= cur_drugbank.fetchone()
    print("drugbankInfo:",drugbankInfo)
    if drugbankInfo != None:
        drugbank_id=drugbankInfo[1]
        #return render_template('drugbankInfomation.html',drugbank_id=drugbank_id)
        return drugbankInfomation(drugbank_id)
    #drugbank_name 查找druginfo
    cur_drugbank_name = conn.cursor()
    sql_drugbank_name="select * from drugbank where drugbank_Name LIKE '%s'" %args
    cur_drugbank_name.execute(sql_drugbank_name)
    drugbankInfo2= cur_drugbank_name.fetchone()
    print("drugbankInfo2:",drugbankInfo2)
    if drugbankInfo2 != None:
        drugbank_id=drugbankInfo2[1]
        return drugbankInfomation(drugbank_id)
    #cas number 查找drugINfo
    cur_cas = conn.cursor()
    sql_cas="select * from drugbank where CAS_number LIKE '%s'" %args
    cur_cas.execute(sql_cas)
    drugbankInfo3= cur_cas.fetchone()
    print("drugbankInfo3:",drugbankInfo3)
    if drugbankInfo3 != None:
        drugbank_id=drugbankInfo3[1]
        return drugbankInfomation(drugbank_id)
    #kegg id 查找 drugINfo
    cur_kegg_id = conn.cursor()
    sql_kegg_id="select * from drugbank where KEGG_Drug LIKE '%s'" %args
    cur_kegg_id.execute(sql_kegg_id)
    drugbankInfo4= cur_kegg_id.fetchone()
    print("drugbankInfo4:",drugbankInfo4)
    if drugbankInfo4 != None:
        drugbank_id=drugbankInfo4[1]
        return drugbankInfomation(drugbank_id)
    #sideName 查找 sideInfo
    cur_side_name = conn.cursor()
    sql_side_name='select * from sider_effect where sideeffect_name LIKE "%s"' %args
    cur_side_name.execute(sql_side_name)
    sideInfo= cur_side_name.fetchone()
    print("sideInfo:",sideInfo)
    if sideInfo != None:
        sideName=sideInfo[1]
        return redirect(url_for('searchForSideName', sideName=sideName))
    #sideeffect_id 查找 sideInfo
    cur_effect_link = conn.cursor()
    sql_effect_link='select * from sider_effect where sideeffect_link LIKE "%s"' %args
    cur_effect_link.execute(sql_effect_link)
    sideInfo2= cur_effect_link.fetchone()
    print("sideInfo2:",sideInfo2)
    if sideInfo2 != None:
        sideName=sideInfo2[1]
        return redirect(url_for('searchForSideName', sideName=sideName))
    #target_name 查找 drugbankTargetInfo
    cur_target_name = conn.cursor()
    sql_target_name='select * from drugbank_target where target_name LIKE "%s"' %args
    cur_target_name.execute(sql_target_name)
    targetInfo2= cur_target_name.fetchone()
    print("targetInfo2:",targetInfo2)
    if targetInfo2 != None:
        target_name=targetInfo2[0]
        return redirect(url_for('searchForTargetName', target_name=target_name))
    #Gene_name 查找 drugbankTargetInfo
    cur_Gene_name = conn.cursor()
    sql_Gene_name='select * from drugbank_target where Gene_Name LIKE "%s"' %args
    cur_Gene_name.execute(sql_Gene_name)
    targetInfo3= cur_Gene_name.fetchone()
    print("targetInfo3:",targetInfo3)
    if targetInfo3 != None:
        target_name=targetInfo3[0]
        return redirect(url_for('searchForTargetName', target_name=target_name))
    #searchForKeggPathway 根据kegg_hsa查找pathway
    cur_kegg_hsa = conn.cursor()
    sql_kegg_hsa='select * from target_pathway where kegg_target_hsa LIKE "%s"' %args
    cur_kegg_hsa.execute(sql_kegg_hsa)
    pathwayInfo= cur_kegg_hsa.fetchone()
    print("pathwayInfo:",pathwayInfo)
    if pathwayInfo != None:
        pathwayHsa=pathwayInfo[0]
        return redirect(url_for('searchForKeggPathway', pathwayHsa=pathwayHsa))
    #searchForKeggPathway 根据 kegg_target_pathway_name 查找pathway
    cur_kegg_target_pathway_name = conn.cursor()
    sql_kegg_target_pathway_name='select * from target_pathway where kegg_target_pathway_name LIKE "%s"' %args
    cur_kegg_target_pathway_name.execute(sql_kegg_target_pathway_name)
    pathwayInfo2= cur_kegg_target_pathway_name.fetchone()
    print("pathwayInfo2:",pathwayInfo2)
    if pathwayInfo2 != None:
        pathwayHsa=pathwayInfo2[0]
        return redirect(url_for('searchForKeggPathway', pathwayHsa=pathwayHsa))
    #searchFordisease 根据 kegg_disease_id 查找disease_Info
    cur_disease_id = conn.cursor()
    sql_disease_id='select * from kegg_disease where kegg_disease_id LIKE "%s"' %args
    cur_disease_id.execute(sql_disease_id)
    diseaseInfo2= cur_disease_id.fetchone()
    print("diseaseInfo2:",diseaseInfo2)
    if diseaseInfo2 != None:
        keggDiseaseId=diseaseInfo2[1]
        return redirect(url_for('searchForKeggDiseaseId', keggDiseaseId=keggDiseaseId))
    #searchFordisease 根据 kegg_disease_Name 查找disease_Info
    cur_disease_name = conn.cursor()
    sql_disease_name='select * from kegg_disease where kegg_disease_name LIKE "%s"' %args
    cur_disease_name.execute(sql_disease_name)
    diseaseInfo3= cur_disease_name.fetchone()
    print("diseaseInfo3:",diseaseInfo3)
    if diseaseInfo3 != None:
        keggDiseaseId=diseaseInfo3[1]
        return redirect(url_for('searchForKeggDiseaseId', keggDiseaseId=keggDiseaseId))
    else:
        return render_template('NotFound.html')

@app.route('/Help')
def Help():
    return render_template('Help.html')

if __name__ == '__main__':
    #getDrugList()
    app.run(port=5009)
