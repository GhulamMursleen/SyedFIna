import flask
import csv
import math
import pandas as pd
from fuzzywuzzy import process,fuzz
from werkzeug.utils import secure_filename
from flask import  abort,request,send_file,jsonify, make_response
from Untitled import Model
model=Model()

from flask_cors import CORS, cross_origin
app = flask.Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config["DEBUG"] = True


@app.route('/', methods=['GET','POST'])
def home():
    return "Api is working for Legal Contracts";
@app.route('/clause/search', methods = [ 'POST'])
def search():
    
   if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
   

   elif request.method == 'POST':
      totalpages=0
      content = request.get_json()
      #print(content)
      Filename="./contractCollection.csv"
      df = pd.read_csv(Filename, error_bad_lines=False)
      df = df.fillna("False")
      result=[]
      clause_category=""
      tag=""
      cont_type=""
      text=""
      
      try:
          #print("try")
          cont_type=content["cont_type"];
          clause_category=content["clause_category"]
          tag=content["tag"];
          
          text=content["text"];
      except:
          return _corsify_actual_response(jsonify({"message":"parameters error"}))
      if cont_type!="" and clause_category!="":
        contain_values = df[df['name'].str.contains(cont_type)   ]
        result=contain_values[df['ClausesCategories'].str.contains(clause_category)]
        if (len(result))==0:
                result=[1,2]
      elif cont_type!="":
            result = df[df['name'].str.contains(cont_type)   ]
            if (len(result))==0:
                result=[1,2]
      elif clause_category!="":
            result=df[df['ClausesCategories'].str.contains(clause_category)]
            if (len(result))==0:
                result=[1,2]
      else:
        result=[1,2]
      #print ("result",len(result))
    
      if len(result)>0:
        Filename="./ClausesCategoriesCollection.csv"
        df2 = pd.read_csv(Filename, error_bad_lines=False)
        df2 = df2.fillna("False")
        claid=df2["_id"].tolist()
        claname=df2["name"].tolist()
        if clause_category!="":#########if category is empty
            contain_values = df2[df2['name'].str.contains(clause_category)   ] ##if caluse category exist
            if len(contain_values)>0:
                 ids=int(contain_values["_id"])
                 Filename="./ClauseCollection.csv"
                 df3 = pd.read_csv(Filename, error_bad_lines=False)
                 df3 = df3.fillna("False")
                 #df3['clauseID']=pd.to_numeric(df3['clauseID'])
                 rows=df3.loc[(df3['tags'] == tag) &(df3['clauseID'] == ids)]
                 data=[]

                 for index, row in rows.iterrows():
                     if (len(data)<10):
                         #print("row",row["_id"])
                         #data.append({"name":row["name"],"description":row["description"]})
                         data.append({"description":row["description"],"clause_type":row["name"],"category":claname[claid.index(row["clauseID"])],"tag":row["tags"],"id":row["_id"],"clauseID":row["clauseID"]})
                 #print("data",data)
                 if len(data)==0:
                      rows=df3.loc[(df3['clauseID'] == ids)]
                      data=[]
                      for index, row in rows.iterrows():
                         if (len(data)<10):
                             #print("row",row["_id"])
                             #print("calid",claid.index(row["clauseID"]))
                             #print("claname",claname[claid.index(row["clauseID"])])
                             #data.append({"name":row["name"],"description":row["description"]})
                             data.append({"description":row["description"],"clause_type":row["name"],"category":claname[claid.index(row["clauseID"])],"tag":row["tags"],"id":row["_id"],"clauseID":row["clauseID"]})
                      array2={"pages":1,"data":data}
                     
                      
                      return _corsify_actual_response(jsonify(array2))
                 array2={"pages":1,"data":data}
                 return _corsify_actual_response(jsonify(array2))
                 ####return data
                 #print("rows",rows,df3.dtypes)
            elif tag!="":  ####################if category does not exist in records but tag exist 
                 #ids=int(contain_values["_id"])
                 Filename="./ClauseCollection.csv"
                 df3 = pd.read_csv(Filename, error_bad_lines=False)
                 df3 = df3.fillna("False")
                 #df3['clauseID']=pd.to_numeric(df3['clauseID'])
                 rows=df3.loc[(df3['tags'] == tag)]
                 data=[]
                 totalpages=math.ceil(len(rows)/10)
                 #print("pages",len(rows),totalpages)
                 for index, row in rows.iterrows():
                     if (len(data)<10):
                         #print("calid",claid.index(row["clauseID"]))
                         #print("claname",claname[claid.index(row["clauseID"])])
                         #print("row",row["_id"])
                         #data.append({"name":row["name"],"description":row["description"]})
                         data.append({"description":row["description"],"clause_type":row["name"],"category":claname[claid.index(row["clauseID"])],"tag":row["tags"],"id":row["_id"],"clauseID":row["clauseID"]})
                     else:
                         break
                 #print("data tag exist",data)
                 array2={"pages":1,"data":data}
                 return _corsify_actual_response(jsonify(array2))
                 ####return data
            elif text!="":#########tag does not exist but text exist
                 Filename="./ClauseCollection.csv"
                 df3 = pd.read_csv(Filename, error_bad_lines=False)
                 df3 = df3.fillna("False")
                 idss=df3['_id'].tolist()
                 entities=df3['name'].tolist()
                 descriptions=df3['description'].tolist()
                 tagss=df3['tags'].tolist()
                 claidss=df3['clauseID'].tolist()
                 results=process.extract(text, descriptions, scorer=fuzz.token_sort_ratio)
                 #print(results)
                 data=[]
                 #print(results[0][0],results[0][1])
                 import random
                 n = random.randint(1,10)
                 totalpages=1
                 #print("pages",totalpages)
                 i=0
                 idz=[]
                 for x in results:
                     if (len(data)<10 and (idss[claid.index(x[1])]+i) not in idz):
                         idz.append(idss[claid.index(x[1])])
                         #data.append({"name":entities[descriptions.index(x[0])],"description":x[0]})
                         try:
                             
                             #print("index",x[1],len(results))
                             #data.append({"name":entities[descriptions.index(x[0])],"description":x[0]})
                             data.append({"description":descriptions[claidss.index(x[1])+i],"clause_type":entities[claidss.index(x[1])+i],"category":claname[claidss[claid.index(x[1])]+i],"tag":tagss[claidss.index(x[1])+i],"id":idss[claidss.index(x[1])+i],"clauseID":x[1]})
                             i=i+1
                             claidss.remove(x[1])
                         except:
                              pass
                     else:
                         break
                 #print("data",data)
                 array2={"pages":1,"data":data}
                 return _corsify_actual_response(jsonify(array2))
            else: ############if text not exist
                #print("g aya no")
                return _corsify_actual_response(jsonify({}))
                
        elif tag!="": ############if clause category does not exist but tag exist
                 Filename="./ClauseCollection.csv"
                 df3 = pd.read_csv(Filename, error_bad_lines=False)
                 df3 = df3.fillna("False")
                 #df3['clauseID']=pd.to_numeric(df3['clauseID'])
                 rows=df3.loc[(df3['tags'] == tag)]
                 data=[]
                 totalpages=math.ceil(len(rows)/10)
                 #print("pages",len(rows),totalpages)
                 for index, row in rows.iterrows():
                     if (len(data)<10):
                         #print("row",row["_id"])
                         #print("calid",claid.index(row["clauseID"]))
                         #print("claname",claname[claid.index(row["clauseID"])])
                         #data.append({"name":row["name"],"description":row["description"]})
                         data.append({"description":row["description"],"clause_type":row["name"],"category":claname[claid.index(row["clauseID"])],"tag":row["tags"],"id":row["_id"],"clauseID":row["clauseID"]})
                 #print("data if tag exist only",len(data))
                 array2={"pages":1,"data":data}
                 return _corsify_actual_response(jsonify(array2))
        elif text!="":#########tag does not exist but text exist
                 Filename="./ClauseCollection.csv"
                 df3 = pd.read_csv(Filename, error_bad_lines=False)
                 df3 = df3.fillna("False")
                 idss=df3['_id'].tolist()
                 entities=df3['name'].tolist()
                 descriptions=df3['description'].tolist()
                 tagss=df3['tags'].tolist()
                 claidss=df3['clauseID'].tolist()
                 results=process.extract(text, descriptions, scorer=fuzz.token_sort_ratio)
                 #print(results)
                 data=[]
                 import random
                 n = random.randint(1,10)
                 totalpages=1
                 #print("pages",totalpages)
                 #print(results[0][0],results[0][1])
                 i=0
                 idz=[]
                 for x in results:
                     if (len(data)<10 and (idss[claid.index(x[1])]+i) not in idz):
                         idz.append(idss[claid.index(x[1])])
                         print("idz",idz)
                         #print("results",results)
                         #print("calid",claid.index(x[1]))
                         #print("claname",claname[claid.index(x[1])])
                         try:
                             
                             #print("index",x[1],len(results))
                             #data.append({"name":entities[descriptions.index(x[0])],"description":x[0]})
                             data.append({"description":descriptions[claidss.index(x[1])+i],"clause_type":entities[claidss.index(x[1])+i],"category":claname[claidss[claid.index(x[1])]+i],"tag":tagss[claidss.index(x[1])+i],"id":idss[claidss.index(x[1])+i],"clauseID":x[1]})
                             i=i+1
                             claidss.remove(x[1])
                         except:
                              pass
                     else:
                         break
                 #print("data",data)
                 array2={"pages":1,"data":data}
                 return _corsify_actual_response(jsonify(array2))
        else: ############if text not exist
            return _corsify_actual_response(jsonify({}))
      #print(clause_category)
      #data = request.values
      #print("coming",request.form["id"])
      
      
      #id=str(request.form["id"])
      #print(id,type(id))
      #response=model.recommendation(id)
      
      
   else:
      return _corsify_actual_response(jsonify({"message":"error"}))
  
#################contracts/types ##########get  no parameter  #################post contract/types   ###########3 parameters
@app.route('/contracts/types', methods = [ 'POST', 'PUT', 'DELETE'])
def requestcontracttypes():
    
   if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
   elif request.method == "PUT":
            newrow=[]
            content = request.get_json()
            try:
                #print("content",content)
                newrow.append(content["id"])
                newrow.append(content["name"])
                newrow.append(content["clausecategories"])
            except:
                return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
            lines=[]
            with open('./contractCollection.csv',encoding='utf8') as readFile:
            
                reader = csv.reader(readFile)
            
                for row in reader:
                    
                    #print(row,type(newrow[0]),type(row[0]))
                    comp=str(newrow[0])
                    if row[0] == comp:
                           print(row,str(newrow[0]),type(row[0]))
                           lines.append(newrow)
                    else:
                        lines.append(row)
                        
            
            with open('contractCollection.csv', 'w',encoding='utf8', newline='') as writeFile:
            
                writer = csv.writer(writeFile)
            
                writer.writerows(lines)
            
                return _corsify_actual_response(jsonify({"message":"Record Updated Successfully"}))
            return _corsify_actual_response(jsonify({"message":"Please Try Again Later!!!!!!!!"}))
   elif request.method == "DELETE":
            content = request.get_json()
            ids=0
            try:
                ids=content["id"]
                
            except:
                return _corsify_actual_response(jsonify({"message":"Parameters error"}))
            lines=[]
            with open('./contractCollection.csv',encoding='utf8') as readFile:
            
                reader = csv.reader(readFile)
            
                for row in reader:
                    
                    print(row,len(row))
                    if len(row)>0 and row[0] == str(ids):
                           pass
                    elif len(row)==0:
                        pass
                    else:
                        lines.append(row)
                        
            
            with open('contractCollection.csv', 'w',encoding='utf8', newline='') as writeFile:
            
                writer = csv.writer(writeFile)
            
                writer.writerows(lines)
            
                return _corsify_actual_response(jsonify({"message":"Record Deleted Successfully"}))
            return _corsify_actual_response(jsonify({"message":"Please Try Again Later!!!!!!!!"}))
   elif request.method == 'POST':
            Filename="./contractCollection.csv"         
            df = pd.read_csv(Filename, usecols = ['_id', 'name'])
            df = df.fillna("False")
            number=3
            totalpages=math.ceil(len(df)/10)
            content = request.get_json()
            
            try:
                number=content["page"]
                number=number-1
                if number<totalpages and number>-1:
                    number=number*10
                else:
                    return _corsify_actual_response(jsonify({"message":"Page does not exist"}))
            except:
                return _corsify_actual_response(jsonify({"message":"Parameters error"}))
            #print("len(df)",len(df),totalpages)
            df = df.iloc[number:]
            #print("len(df)",len(df),totalpages)
            array=[]
            for index, row in df.iterrows() :
                if len(array) <10:
                    array.append({"id":row[0],"name":row[1]})
                else:
                    break
            array={"pages":totalpages,"data":array}
            #print(array)
      
            return _corsify_actual_response(jsonify(array))
            """
   elif request.method == 'POST':
          row=[]
          content = request.get_json()
          Filename="./contractCollection.csv"
          df3 = pd.read_csv(Filename, error_bad_lines=False)
          inserted=len(df3)+1
          try:
                row.append(len(df3)+1)
                row.append(content["name"])
                row.append(content["clausecategories"])
          except:
                return _corsify_actual_response(jsonify({"message":"Parameters error"}))
          with open("./contractCollection.csv",encoding='utf8', mode='a+', newline='') as Data:
                employee_writer = csv.writer(Data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                employee_writer.writerow(row)
                return _corsify_actual_response(jsonify({"insertid":inserted,"message":"successful"}))
          
          return _corsify_actual_response(jsonify({"message":"Please try again!!!!!"}))"""
   
   else:
      return _corsify_actual_response(jsonify({"message":"Please try again!!!!!"}))

#################clause/categories ##########get  no parameter  #################caluse/categories post  ###########add no parameter 
@app.route('/clause/categories', methods = ['POST', 'PUT', 'DELETE'])
def calusecategories():
    
   if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
   elif request.method == "PUT":
            newrow=[]
            content = request.get_json()
            try:
                print("content",content)
                newrow.append(content["id"])
                newrow.append(content["name"])
            except:
                return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
            lines=[]
            with open('./ClausesCategoriesCollection.csv',encoding='utf8') as readFile:
            
                reader = csv.reader(readFile)
            
                for row in reader:
                    
                    print(row,len(row))
                    comp=str(newrow[0])
                    if row[0] == comp:
                           lines.append(newrow)
                    else:
                        lines.append(row)
                        
            
            with open('ClausesCategoriesCollection.csv', 'w',encoding='utf8', newline='') as writeFile:
            
                writer = csv.writer(writeFile)
            
                writer.writerows(lines)
            
                return _corsify_actual_response(jsonify({"message":"Record Updated Successfully"}))
            return _corsify_actual_response(jsonify({"message":"Please Try Again Later!!!!!!!!"}))
   elif request.method == "DELETE":
            content = request.get_json()
            ids=0
            try:
                ids=content["id"]
                
            except:
                return _corsify_actual_response(jsonify({"message":"Parameters error"}))
            lines=[]
            with open('./ClausesCategoriesCollection.csv',encoding='utf8') as readFile:
            
                reader = csv.reader(readFile)
            
                for row in reader:
                    
                    print(row,len(row))
                    if len(row)>0 and row[0] == str(ids):
                           pass
                    elif len(row)==0:
                        pass
                    else:
                        lines.append(row)
                        
            
            with open('ClausesCategoriesCollection.csv', 'w',encoding='utf8', newline='') as writeFile:
            
                writer = csv.writer(writeFile)
            
                writer.writerows(lines)
            
                return _corsify_actual_response(jsonify({"message":"Record Deleted Successfully"}))
            return _corsify_actual_response(jsonify({"message":"Please Try Again Later!!!!!!!!"}))
   elif request.method == 'POST':
            Filename="./ClausesCategoriesCollection.csv"         
            df = pd.read_csv(Filename, usecols = ['_id', 'name'])
            df = df.fillna("False")
            #json = df.to_dict
            number=3
            totalpages=math.ceil(len(df)/10)
            content = request.get_json()
            
            try:
                number=content["page"]
                number=number-1
                if number<totalpages and number>-1:
                    
                    number=number*10
                else:
                    return _corsify_actual_response(jsonify({"message":"Page does not exist"}))
            except:
                return _corsify_actual_response(jsonify({"message":"Parameters error"}))
            #print("len(df)",len(df),totalpages)
            df = df.iloc[number:]
            #print("len(df)",len(df),totalpages)
            array=[]
            for index, row in df.iterrows() :
                if len(array) <10:
                    array.append({"id":row[0],"name":row[1]})
                else:
                    break
            array={"pages":totalpages,"data":array}
            #print(array)
      
            return _corsify_actual_response(jsonify(array))
            """
   elif request.method == 'POST':
            row=[]
            content = request.get_json()
            Filename="./ClausesCategoriesCollection.csv"
            df3 = pd.read_csv(Filename, error_bad_lines=False)
            inserted=len(df3)+1
            try:
                row.append(len(df3)+1)
                row.append(content["name"])
            except:
                return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
            #row.append(request.form["id"])
            #row.append(request.form["name"])
            #row.append(15)
            #row.append("Mursleen")
            
            with open("./ClausesCategoriesCollection.csv",encoding='utf8', mode='a+', newline='') as Data:
                            employee_writer = csv.writer(Data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                            employee_writer.writerow(row)
                            print('done')
                            return _corsify_actual_response(jsonify({"insertid":inserted,"message":"successful"}))
      
            return _corsify_actual_response(jsonify({"message":"Please try again"}))"""
   
   else:
      return _corsify_actual_response(jsonify({"message":"Please try again"}))
#################clause/tags ##########get  no parameter only get
@app.route('/clause/tags', methods = ['GET', 'POST'])
def clausetags():
    
   if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
   elif request.method == 'GET':
            Filename="./ClauseCollection.csv"         
            df = pd.read_csv(Filename, usecols = [ 'tags'])
            df=df.drop_duplicates()
            df=df.drop_duplicates()
            df=df.dropna()
            #values = df.unique()
            #print("values",df)
            
            array3=[]
            for index, row in df.iterrows() :
                array3.append({"tag":row[0]})
            #print(array3)
            return _corsify_actual_response(jsonify(array3))
   
   else:
      return _corsify_actual_response(jsonify({"message":"Please try again!!!!!error"}))
#################train
@app.route('/model/train', methods = ['GET', 'POST'])
def train():
    
   if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
   elif request.method == 'GET':
            
            res=model.train()
            #print(array3)
            return _corsify_actual_response(jsonify(res))
   
   else:
      return _corsify_actual_response(jsonify({"message":"Please try again!!!!!error"}))
#################predict
@app.route('/model/predict', methods = ['GET', 'POST'])
def predict():
    
   if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
   elif request.method == 'POST':
            content = request.get_json()
            data=[]
            try:
                print("content",content)
                data=content["data"]
                
            except:
                return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
            result=model.predict(data)
            #res={"data":data,"prediction":result}
            #print(array3)
            return _corsify_actual_response(jsonify(result))
   
   else:
      return _corsify_actual_response(jsonify({"message":"Please try again!!!!!error"}))
#################predict
@app.route('/clause/add/detail', methods = ['GET', 'POST'])
def complete():
    
   if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
   elif request.method == 'POST':
            content = request.get_json()
            
            
            data={}
            try:
               
                #print("content",content)
                datas={"clausename":content["clausename"],#Ending Text
                    "contracttype":content["contracttype"],
                    "category":content["category"],
                    "tag":content["tag"],
                    "clausetext":content["clausetext"]}
                data=datas
                print("data",data)
                
                if content["clausename"]=="" or content["contracttype"]=="" or content["category"]=="" or content["tag"]=="" or content["clausetext"]=="":
                    return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters can't be empty"}))
                
            except:
                return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
            
            
            df = pd.read_csv("./contractCollection.csv")
            ###name
            ###ClausesCategories
            ##print(df.head())
            contracts=df['name'].tolist()
            clauses=df['ClausesCategories'].tolist()
            
            if data["contracttype"] in contracts:
                
                #print("yes",contracts.index(data["contracttype"]))
                if data["category"] in clauses[contracts.index(data["contracttype"])]:
                        #print("type exist")
                        df2 = pd.read_csv("./ClausesCategoriesCollection.csv")
                        idxx=df2['_id'].tolist()
                        types=df2['name'].tolist()
                        id=1000
                        if data["category"] in types:
                            id=idxx[types.index(data["category"])]
                        else:
                            print("not exist id",types)
                            row=[]
                            
                            Filename="./ClausesCategoriesCollection.csv"
                            df3 = pd.read_csv(Filename, error_bad_lines=False)
                            inserted=len(df3)+1
                            id=inserted
                            try:
                                    row.append(len(df3)+1)
                                    row.append(data["category"])
                            except:
                                    return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
                                    
                                
                            with open("./ClausesCategoriesCollection.csv",encoding='utf8', mode='a+', newline='') as Data:
                                                employee_writer = csv.writer(Data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                                employee_writer.writerow(row)
                                                print('done')
                                                
                        df3 = pd.read_csv("./ClauseCollection.csv")
                        df3=df3.astype(str)
                        df3.head()
                        rows=df3.loc[(df3['name'] == data["clausename"]) & (df3['description'] == data["clausetext"])&(df3['tags'] == data["tag"])&(df3['clauseID'] == str(id)) ]
                        
                        if len(rows)==0:
                            
                            
                            row=[]
                            Filename="./ClauseCollection.csv"
                            df3 = pd.read_csv(Filename, error_bad_lines=False)
                            inserted=len(df3)+1
                            try:
                                row.append(len(df3)+1)
                                row.append(data["clausename"])
                                row.append(data["clausetext"])
                                row.append(data["tag"])
                                row.append(id)
                            except:
                                return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
                                
                            
                            with open("./ClauseCollection.csv",encoding='utf8', mode='a+', newline='') as Data:
                                            employee_writer = csv.writer(Data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                            employee_writer.writerow(row)
                                            #print('done')
                                            #return _corsify_actual_response(jsonify("success"))
                                            return _corsify_actual_response(jsonify({"insertid":inserted,"message":"successful"}))
                        else:
                            return _corsify_actual_response(jsonify({"message":"Record Already Exist"}))
                    
                else:
                    #print("notexist",)
                    clauses[contracts.index(data["contracttype"])]=clauses[contracts.index(data["contracttype"])][0:len(clauses[contracts.index(data["contracttype"])])-1]+", '"+data["category"]+"']"
                    #print("notexist",clauses[contracts.index(data["contracttype"])])
                    df2 = pd.read_csv("./ClausesCategoriesCollection.csv")
                    idxx=df2['_id'].tolist()
                    types=df2['name'].tolist()
                    id=1000
                    if data["category"] in types:
                            id=idxx[types.index(data["category"])]
                    else:
                            #print("not exist id",types)
                            row=[]
                            
                            Filename="./ClausesCategoriesCollection.csv"
                            df3 = pd.read_csv(Filename, error_bad_lines=False)
                            inserted=len(df3)+1
                            id=inserted
                            try:
                                    row.append(len(df3)+1)
                                    row.append(data["category"])
                            except:
                                    return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
                                    
                                
                            with open("./ClausesCategoriesCollection.csv",encoding='utf8', mode='a+', newline='') as Data:
                                                employee_writer = csv.writer(Data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                                employee_writer.writerow(row)
                                                #print('done')
                    df3 = pd.read_csv("./ClauseCollection.csv")
                    df3=df3.astype(str)
                    df3.head()
                    rows=df3.loc[(df3['name'] == data["clausename"]) & (df3['description'] == data["clausetext"])&(df3['tags'] == data["tag"])&(df3['clauseID'] == str(id)) ]
                        
                    if len(rows)==0:
                            
                            
                        row=[]
                        Filename="./ClauseCollection.csv"
                        df3 = pd.read_csv(Filename, error_bad_lines=False)
                        inserted=len(df3)+1
                        try:
                                row.append(len(df3)+1)
                                row.append(data["clausename"])
                                row.append(data["clausetext"])
                                row.append(data["tag"])
                                row.append(id)
                        except:
                                return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
                                
                            
                        with open("./ClauseCollection.csv",encoding='utf8', mode='a+', newline='') as Data:
                                            employee_writer = csv.writer(Data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                            employee_writer.writerow(row)
                                            #print('done')
                                            #return _corsify_actual_response(jsonify({"message":"Please try again"}))"""
                                            df['ClausesCategories']=pd.DataFrame({'ClausesCategories':clauses})
                                            df.to_csv('contractCollection.csv', index=False)
                                            return _corsify_actual_response(jsonify({"insertid":inserted,"message":"successful"}))
                    else:
                            return _corsify_actual_response(jsonify({"message":"Record Already Exist"}))  
                        
            else:########if contract not exist contract and clause added
                      row=[]
                      Filename="./contractCollection.csv"
                      df3 = pd.read_csv(Filename, error_bad_lines=False)
                      inserted=len(df3)+1
                      try:
                            row.append(len(df3)+1)
                            row.append(data["contracttype"])
                            row.append("['"+data["category"]+"']")
                      except:
                            return _corsify_actual_response(jsonify({"message":"Parameters error"}))
                            
                      with open("./contractCollection.csv",encoding='utf8', mode='a+', newline='') as Data:
                            employee_writer = csv.writer(Data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                            employee_writer.writerow(row)
                            
                            df2 = pd.read_csv("./ClausesCategoriesCollection.csv")
                            idxx=df2['_id'].tolist()
                            types=df2['name'].tolist()
                            id=1000
                            if data["category"] in  types:
                                id=idxx[types.index(data["category"])]
                            else:
                                row=[]
                                
                                Filename="./ClausesCategoriesCollection.csv"
                                df3 = pd.read_csv(Filename, error_bad_lines=False)
                                inserted=len(df3)+1
                                id=inserted
                                try:
                                        row.append(len(df3)+1)
                                        row.append(data["category"])
                                except:
                                        return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
                                        
                                    
                                with open("./ClausesCategoriesCollection.csv",encoding='utf8', mode='a+', newline='') as Data:
                                                    employee_writer = csv.writer(Data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                                    employee_writer.writerow(row)
                                                    #print('done')
                            df3 = pd.read_csv("./ClauseCollection.csv")
                            df3=df3.astype(str)
                            df3.head()
                            rows=df3.loc[(df3['name'] == data["clausename"]) & (df3['description'] == data["clausetext"])&(df3['tags'] == data["tag"])&(df3['clauseID'] == str(id)) ]
                            
                            if len(rows)==0:
                                row=[]
                                Filename="./ClauseCollection.csv"
                                df3 = pd.read_csv(Filename, error_bad_lines=False)
                                inserted=len(df3)+1
                                try:
                                    row.append(len(df3)+1)
                                    row.append(data["clausename"])
                                    row.append(data["clausetext"])
                                    row.append(data["tag"])
                                    row.append(id)
                                except:
                                    return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
                                    
                               
                                
                                with open("./ClauseCollection.csv",encoding='utf8', mode='a+', newline='') as Data:
                                                employee_writer = csv.writer(Data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                                employee_writer.writerow(row)
                                                #print('done')
                                                return _corsify_actual_response(jsonify({"insertid":id,"message":"successful"}))
                            else:
                                return _corsify_actual_response(jsonify({"message":"Record Already Exist"}))
                        
                            
                        
                        
                        
                        
                        
                        
            
            
            
            
            
            
            
   
   else:
      return _corsify_actual_response(jsonify({"message":"Please try again!!!!!error"}))

#################Similar
@app.route('/model/search', methods = ['GET', 'POST'])
def msearch():
    
   if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
   elif request.method == 'POST':
            content = request.get_json()
            data=[]
            try:
                print("content",content)
                data=content["data"]
                
            except:
                return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
           
            Filename="./ClauseCollection.csv"
            df = pd.read_csv(Filename,usecols=['description','tags'],  error_bad_lines=False)
            df = df.dropna()
            descriptions=df['description'].tolist()
            result=[]
            results=process.extract(data, descriptions, scorer=fuzz.token_sort_ratio)
            for x in results:
                if len(result)<10:
                #print("results",results[0])
                    result.append(x[0])
                else:
                    break
            #result = loaded_model.predict(X)
            
            res={"clauses":result}
            #print(array3)
            return _corsify_actual_response(jsonify(res))
   
   else:
      return _corsify_actual_response(jsonify({"message":"Please try again!!!!!error"}))
#################caluse/categories post  ###########add no parameter
@app.route('/legal/clauses', methods = ['GET','POST', 'PUT', 'DELETE'])
def legalclauses():
    
   if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
   elif request.method == "PUT":
            newrow=[]
            content = request.get_json()
            try:
                print("content",content)
                newrow.append(content["id"])
                newrow.append(content["name"])
                newrow.append(content["text"])
                newrow.append(content["tags"])
                newrow.append(content["clauseid"])
            except:
                return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
            lines=[]
            with open('./ClauseCollection.csv',encoding='utf8') as readFile:
            
                reader = csv.reader(readFile)
            
                for row in reader:
                    
                    print(row,len(row))
                    if row[0] == str(newrow[0]):
                           lines.append(newrow)
                    else:
                        lines.append(row)
                        
            
            with open('ClauseCollection.csv', 'w',encoding='utf8', newline='') as writeFile:
            
                writer = csv.writer(writeFile)
            
                writer.writerows(lines)
            
                return _corsify_actual_response(jsonify({"message":"Record Updated Successfully"}))
            return _corsify_actual_response(jsonify({"message":"Please Try Again Later!!!!!!!!"}))
   elif request.method == "DELETE":
            content = request.get_json()
            ids=0
            try:
                ids=content["id"]
                
            except:
                return _corsify_actual_response(jsonify({"message":"Parameters error"}))
            lines=[]
            with open('./ClauseCollection.csv',encoding='utf8') as readFile:
            
                reader = csv.reader(readFile)
            
                for row in reader:
                    
                    print(row,len(row))
                    if len(row)>0 and row[0] == str(ids):
                           pass
                    elif len(row)==0:
                        pass
                    else:
                        lines.append(row)
                        
                        
            
            with open('ClauseCollection.csv', 'w',encoding='utf8', newline='') as writeFile:
            
                writer = csv.writer(writeFile)
            
                writer.writerows(lines)
            
                return _corsify_actual_response(jsonify({"message":"Record Deleted Successfully"}))
            return _corsify_actual_response(jsonify({"message":"Please Try Again Later!!!!!!!!"}))
   elif request.method == 'POST':
            Filename="./ClauseCollection.csv"         
            df = pd.read_csv(Filename, usecols = ['_id', 'name','description','tags','clauseID'])
            df = df.fillna("False")
            #json = df.to_dict
            number=3
            totalpages=math.ceil(len(df)/10)
            content = request.get_json()
            
            try:
                number=content["page"]
                number=number-1
                if number<totalpages and number>-1:
                    number=number*10
                else:
                    return _corsify_actual_response(jsonify({"message":"Page does not exist"}))
            except:
                return _corsify_actual_response(jsonify({"message":"Parameters error"}))
            #print("len(df)",len(df),totalpages)
            df = df.iloc[number:]
            #print("len(df)",len(df),totalpages)
            array=[]
            for index, row in df.iterrows() :
                if len(array) <10:
                    array.append({"id":row[0],"name":row[1],"description":row[2],"tags":row[3],"clauseid":row[4]})
                else:
                    break
            array={"pages":totalpages,"data":array}
            #print(array)
      
            return _corsify_actual_response(jsonify(array))
            """
   elif request.method == 'POST':
            content = request.get_json()
            row=[]
            Filename="./ClauseCollection.csv"
            df3 = pd.read_csv(Filename, error_bad_lines=False)
            inserted=len(df3)+1
            try:
                row.append(len(df3)+1)
                row.append(content["name"])
                row.append(content["text"])
                row.append(content["tags"])
                row.append(content["clauseid"])
            except:
                return _corsify_actual_response(jsonify({"message":"Please try again!!!!! Parameters error"}))
            #row.append(15)
            #row.append("Mursleen")
            #row.append("Mursleen")
            #row.append("Mursleen")
            #row.append(15)
            
            with open("./ClauseCollection.csv",encoding='utf8', mode='a+', newline='') as Data:
                            employee_writer = csv.writer(Data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                            employee_writer.writerow(row)
                            print('done')
                            #return _corsify_actual_response(jsonify("success"))
                            return _corsify_actual_response(jsonify({"insertid":inserted,"message":"successful"}))
            return _corsify_actual_response(jsonify({"message":"error"}))"""
   
   else:
      return _corsify_actual_response(jsonify({"message":"Please try again!!!!! error"}))
#####################mergecall
@app.route('/clause/category/merge', methods = ['GET', 'POST'])
def merge():
    
   if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
   elif request.method == 'GET':
                
                print("merge")
                  #################contract types
                Filename="./contractCollection.csv"         
                df = pd.read_csv(Filename, usecols = ['_id', 'name','ClausesCategories'])
                df = df.fillna("False")
                df = df.drop_duplicates(subset = ["name"])
                #json = df.to_dict
                array={}
                for index, row in df.iterrows() :
                        print(row[2][1:len(row[2])].split(","))
                        array.update({row[1]:row[2][1:len(row[2])-1].replace(" '","").replace("'","").split(",")})
                    
                
                #{"contractObject":array}
                
                #print(array)
                """
                        #################clause categories
                Filename="./ClausesCategoriesCollection.csv"         
                df = pd.read_csv(Filename, usecols = ['_id', 'name'])
                df = df.fillna("False")
                
                #json = df.to_dict
                
                array2=[]
                for index, row in df.iterrows() :
                    
                        array2.append({row[1]:row[2]})
                 """
                
                #{"ClausesObject":array2}

                #print(array2)
                
                        #################clause tags
                Filename="./ClauseCollection.csv"         
                
                df = pd.read_csv(Filename, usecols = [ 'tags'])
                df=df.dropna()
                df = df.fillna("False")
                df=df.drop_duplicates()
                df=df.drop_duplicates()
                df=df.dropna()
                
                #values = df.unique()
                #print("values",df)
                
                array3=[]
                for index, row in df.iterrows() :
                    array3.append({"id":index,"tag":row[0]})
                #print(array3)
                
                
                #############################mergeall
                result={"contractType":array,"tag":array3}
                #print(merge)
                return _corsify_actual_response(jsonify(result))
  
   
   else:
      return _corsify_actual_response(jsonify({"message":"Please try again!!!!! error"}))
def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run( port = 3000, threaded=True,debug=True, use_reloader=True)