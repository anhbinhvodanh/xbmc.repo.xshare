﻿# -*- coding: utf-8 -*-
import xbmc,xbmcplugin,xbmcgui,xbmcaddon,urllib,re,os,unicodedata,datetime,random,json

myaddon = xbmcaddon.Addon(); home = myaddon.getAddonInfo('path')
icon_path = xbmc.translatePath(os.path.join( home,'resources/media/'))
data_path = xbmc.translatePath(os.path.join( home,'resources/data/'))
datapath = xbmc.translatePath(os.path.join( xbmc.translatePath(myaddon.getAddonInfo('profile')),'data/'))
sys.path.append(xbmc.translatePath(os.path.join(home, 'resources', 'lib')));import urlfetch
thumucrieng = 'https://www.fshare.vn/folder/'+myaddon.getSetting('thumucrieng').upper()
thumuccucbo =  myaddon.getSetting('thumuccucbo');copyxml = myaddon.getSetting('copyxml')
phim18 = myaddon.getSetting('phim18');search_file=os.path.join(datapath,"search.xml")
rows = int(myaddon.getSetting('sodonghienthi'))
googlesearch = myaddon.getSetting('googlesearch')

media_ext=['aif','iff','m3u','m4a','mid','mp3','mpa','ra','wav','wma','3g2','3gp','asf','asx','avi','flv','mov','mp4','mpg','mkv','m4v','rm','swf','vob','wmv','bin','cue','dmg','iso','mdf','toast','vcd','ts','flac']
hd = {'User-Agent' : 'Mozilla/5.0 Chrome/39.0.2171.71 Firefox/33.0'}
color={'fshare':'[COLOR gold]','vaphim':'[COLOR gold]','phimfshare':'[COLOR khaki]','4share':'[COLOR blue]','tenlua':'[COLOR fuchsia]','fptplay':'[COLOR orange]','trangtiep':'[COLOR lime]','search':'[COLOR lime]','ifile':'[COLOR blue]','hdvietnam':'[COLOR crimson]','xshare':'[COLOR blue]','subscene':'[COLOR green]','megabox':'[COLOR orangered]','dangcaphd':'[COLOR yellow]'}
icon={'icon':icon_path+'icon.png','fshare':icon_path+'fshare.png','vaphim':icon_path+'fshare.png','phimfshare':icon_path+'fshare.png','ifile':icon_path+'4share.png','4share':icon_path+'4share.png','tenlua':icon_path+'tenlua.png','hdvietnam':icon_path+'hdvietnam.png','khophim':icon_path+'khophim.png','xshare':icon_path+'icon.png','fptplay':icon_path+'fptplay.png','megabox':icon_path+'megabox.png','dangcaphd':icon_path+'dangcaphd.png'}

def mess(message, timeShown=5000):
	xbmc.executebuiltin((u'XBMC.Notification(%s,%s,%s,%s)'%('Xshare',message,timeShown,icon_path+'icon.png')).encode("utf-8"))

if not os.path.exists(thumuccucbo):
	thumuccucbo=xbmc.translatePath( os.path.join(data_path,'list_xml/'))
	mess(u'Bạn hãy set "thư mục cục bộ"')

def init_file():
	if not os.path.exists(xbmc.translatePath(myaddon.getAddonInfo('profile'))):
		os.mkdir(xbmc.translatePath(myaddon.getAddonInfo('profile')))
	if not os.path.exists(datapath):os.mkdir(datapath)
	xmlheader='<?xml version="1.0" encoding="utf-8">\n';p=datapath;q=thumuccucbo
	for i in [(p,'search.xml'),(p,'hdvietnam.xml'),(p,'favourites.xml'),(q,'mylist.xml')]:
		if not os.path.isfile(os.path.join(i[0],i[1])):
			if not makerequest(os.path.join(i[0],i[1]),string=xmlheader,attr='w'):
				mess(u'Không tạo được file %s'%i[1])
	if not os.path.exists(os.path.join(thumuccucbo,'temp')):
		os.mkdir(os.path.join(thumuccucbo,'temp'))

def mess_yesno(title='Xshare', line1='Are you ready ?', line2=''):
	dialog = xbmcgui.Dialog()#dialog.yesno(heading, line1[, line2, line3,nolabel,yeslabel])
	return dialog.yesno(title,line1,line2)

def no_accent(s):
	s=re.sub(u'Đ','D',str2u(s));s=re.sub(u'đ','d',s)
	return unicodedata.normalize('NFKD', unicode(s)).encode('ASCII', 'ignore')

def str2u(s):
	try:
		if type(s)==str:s=s.decode('utf-8')
	except:mess('decode error');pass
	return s

def xshare_group(object,group):
	if object:temp=object.group(group)
	else:temp=''
	return temp

def xbmcsetResolvedUrl(url):
	item = xbmcgui.ListItem(path=url)
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

def addir(name,link,img='',fanart='',mode=0,page=0,query='',isFolder=False):
	ok=True;name=re.sub(',|\|.*\||\||\<.*\>','',name)
	item = xbmcgui.ListItem(name,iconImage=img,thumbnailImage=img)
	query=menuContext(name,link,img,fanart,mode,query,item)
	item.setInfo(type="Video", infoLabels={"title":name})
	item.setProperty('Fanart_Image',fanart)
	u=sys.argv[0]+"?url="+urllib.quote_plus(link)+"&img="+urllib.quote_plus(img)+"&fanart="+urllib.quote_plus(fanart)+"&mode="+str(mode)+"&page="+str(page)+"&query="+query+"&name="+name
	if not isFolder:item.setProperty('IsPlayable', 'true')
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=isFolder)
	return ok

def addirs(name,href,img='',fanart='',query=''):
	name=clean_string(name)
	if '18+' in name and phim18=="false":return
	if not fanart and icon_path not in img:fanart=img
	if 'xml' in query:
		if name=='mylist.xml':name=color['subscene']+name+'[/COLOR]'
		query=query.replace('xml','');name='%sList xml[/COLOR]-%s'%(color['fptplay'],name)
		addir(name,href,img,fanart,mode=97,query=query,isFolder=True)
	elif query=='file':addir(name,href,img=icon['icon'],mode=96,query=query,isFolder=True)
	elif 'www.fshare.vn/file' in href:
		if 'phụ đề việt' in name.lower():
			name=color['fshare']+'Fshare Phụ đề Việt[/COLOR]-%s'%name
			addir(name,href,img,fanart,mode=3,query=query,isFolder=True)
		else:addir(color['fshare']+'Fshare[/COLOR]-%s'%name,href,img,fanart,mode=3,query=query)
	elif 'www.fshare.vn/folder' in href:
		if 'Mục chia sẻ của' in name:name=color['trangtiep']+name+'[/COLOR]'
		else:name=color['fshare']+name+'[/COLOR]'
		addir(name,href,img,fanart,mode=90,query=query,isFolder=True)
	elif '4share.vn/d/' in href:
		addir(color['4share']+name+'[/COLOR]',href,img,fanart,mode=38,query=query,isFolder=True)
	elif '4share.vn' in href:
		addir(color['4share']+'4share[/COLOR]-%s'%name,href,img,fanart,mode=3,query=query)
	elif 'tenlua.vn/fm/folder/' in href or '#download' in href:
		addir(color['tenlua']+name+'[/COLOR]',href,img,fanart,mode=95,query=query,isFolder=True)
	elif 'tenlua.vn' in href:
		addir(color['tenlua']+'TenLua[/COLOR]-%s'%name,href,img,fanart,mode=3,query=query)
	elif 'subscene.com' in href:
		addir(color['subscene']+'Subscene[/COLOR]-%s'%name,href,img,fanart,mode=94,query='download',isFolder=True)

def menuContext(name,link,img,fanart,mode,query,item):
	if query.split('?')[0]=='Search':
		query=query.split('?')[1]
		item.addContextMenuItems(searchContext(name,link,img,fanart,mode))
	elif query.split('?')[0]=='ID':
		query=query.split('?')[1]
		command=searchContext(name,link,img,fanart,15)
		command+=favouritesContext(name,link,img,fanart,mode)
		item.addContextMenuItems(command)
	elif 'fshare.vn' in link or '4share.vn' in link or 'tenlua.vn' in link:#mode in (3,38,90,95):
		item.addContextMenuItems(favouritesContext(name,link,img,fanart,mode))
	elif thumuccucbo in link:
		item.addContextMenuItems(make_myFile(name,link,img,fanart,mode,query))
	return query

def makeContext(name,link,img,fanart,mode,query):
	make=query.split()[0]
	if make=='Rename':colo=color['fshare']
	elif make=='Remove':colo=color['hdvietnam']
	else:colo=color['trangtiep']
	context=colo+query+'[/COLOR]'
	p=(myaddon.getAddonInfo('id'),mode,name,link,img,fanart,make)
	cmd='RunPlugin(plugin://%s/?mode=%d&name=%s&url=%s&img=%s&fanart=%s&query=%s)'%(p)
	return context,cmd

def searchContext(name,link,img,fanart,mode):
	command=[(makeContext(name,link,img,fanart,9,'Rename item'))]
	command.append((makeContext(name,link,img,fanart,9,'Remove item')))
	return command
	
def favouritesContext(name,link,img,fanart,mode):
	command=[]
	if link in makerequest(os.path.join(datapath,"favourites.xml")):
		command.append((makeContext(name,link,img,fanart,98,'Rename in MyFavourites')))
		command.append((makeContext(name,link,img,fanart,98,'Remove from MyFavourites')))
	else:
		command.append((makeContext(name,link,img,fanart,98,'Add to MyFavourites')))
	if 'www.fshare.vn' in link:
		if query=='thumucrieng':
			command.append((makeContext(name,link,img,fanart,11,'Remove from MyFshare')))
			command.append((makeContext(name,link,img,fanart,11,'Rename from MyFshare')))
		else:
			command.append((makeContext(name,link,img,fanart,11,'Add to MyFshare')))
	if link in makerequest(os.path.join(thumuccucbo,'mylist.xml')):
		command.append((makeContext(name,link,img,fanart,12,'Rename in Mylist.xml')))
		command.append((makeContext(name,link,img,fanart,12,'Remove from Mylist.xml')))
	else:
		command.append((makeContext(name,link,img,fanart,12,'Add to Mylist.xml')))
	return command

def make_myFile(name,link,img,fanart,mode,query):
	name=re.sub('\[COLOR.{,12}\]|\[/COLOR\]|Fshare|4share|TenLua|List xml|-|:|"','',name).strip();command=[]
	if os.path.isfile(str2u(link)):
		command.append((makeContext(name,link,img,fanart,11,'Upload to MyFshare')));temp='file'
	else:temp='folder'
	command.append((makeContext(name,link,img,fanart,96,'Rename this %s'%temp)))
	command.append((makeContext(name,link,img,fanart,96,'Remove this %s'%temp)))
	return command

def make_mySearch(name,url,img,fanart,mode,query):
	name=re.sub('\[COLOR.{,12}\]|\[/COLOR\]|Fshare|4share|TenLua|List xml|-|:|"','',name).strip()
	if query=='Rename':
		string=get_input('Nhập chuổi mới',name).strip()
		if not string or string==name:return
		string= ' '.join(s for s in string.replace('"',"'").replace('?','').split() if s)
		if re.search('http.?://',url):
			body=re.sub('<a href="%s">.+?</a>'%url,'<a href="%s">%s</a>'%(url,string),makerequest(search_file))
		else:body=re.sub('<a>%s</a>'%name,'<a>%s</a>'%string,makerequest(search_file))
	elif query=='Remove':
		if re.search('http.?://',url):
			body=re.sub('<a href="%s">.+?</a>\n'%url,'',makerequest(search_file))
		else:body=re.sub('<a>%s</a>\n'%name,'',makerequest(search_file))
	if makerequest(search_file,string=body,attr='w'):
		mess(u'%s chuổi thành công'%query);xbmc.executebuiltin("Container.Refresh")
	else:mess(u'%s chuổi thất bại'%query)
	return

def make_myFshare(name,url,img,fanart,mode,query):#11
	myFshare=myaddon.getSetting('thumucrieng')
	if not myFshare or (myFshare=='RDA4FHXVE2UU' and myaddon.getSetting('usernamef')!='thai@thanhthai.net'):
		mess(u'Hãy set "Thư mục chia sẻ của tôi trên Fshare"');return
	elif query=='Add':
		href='https://www.fshare.vn/api/fileops/createFolder'
		title=xshare_group(re.search('(\w{10,20})',url),1)
		if title:
			title+=' %s'%re.sub('\[COLOR.{,12}\]|\[/COLOR\]|Fshare|4share|TenLua|List xml|-|:|"','',name)
			title=re.sub('.xml.*','.xml',title)
		else:mess(u'Nhận dạng link bị lỗi');return
	elif query=='Rename':
		href='https://www.fshare.vn/api/fileops/rename'
		body = make_request('https://www.fshare.vn/folder/%s'%myFshare)
		title=re.sub('\[COLOR.{,12}\]|\[/COLOR\]|Fshare|4share|TenLua|List xml|-|:|"','',name)
		id=re.search('data-id="(.+?)".*>(.*%s.*)</a></div>'%title,body)
		if id:old_name=id.group(2);id=id.group(1)
		else:return
		new_name=get_input('Sửa tên 1 mục trong MyFshare',title).strip()
		if not new_name or new_name==title:return
		else:new_name=re.sub(title,new_name,old_name)
	elif query=='Remove':
		href='https://www.fshare.vn/api/fileops/delete'
		id=os.path.basename(url);folder=False
		body = make_request('https://www.fshare.vn/folder/%s'%myFshare)
		for data_id,data_type,data_path in re.findall('data-id="(.+?)" data-type="(.+?)" data-path="(.+?)"',body):
			if data_id==id and data_type=='folder':folder=True;break
			elif id in data_path:id=data_id;break
		if folder:
			line1='Thư mục: %s'%name
			line2='Có thể có dữ liệu quan trọng của bạn! %sBạn muốn xóa không?[/COLOR]'%color['tenlua']
			traloi=mess_yesno('Xshare - Cảnh báo nguy hiểm!',line1,line2)
			if traloi==0:mess(u'OK ! xshare chưa làm gì cả!'); return
	elif query=='Upload':
		href='https://www.fshare.vn/api/session/upload'
		try:size=os.path.getsize(str2u(url))
		except:pass
		if size>10**7:mess(u'Add-on chưa hỗ trợ upload file>10MB');return
		try:f=open(str2u(url),'rb');content=f.read();f.close()
		except:mess(u'Không đọc được file %s'%str2u(url));return
	
	hd['Cookie'] = loginfshare()
	if not hd['Cookie']:return
	body = make_request('https://www.fshare.vn/home', headers=hd)
	token=xshare_group(re.search('data-token="(.+?)"',body),1)
	if query=='Add':
		data='{"token":"%s","name":"%s","in_dir":"%s"}'%(token,title,myaddon.getSetting('thumucrieng'))
		noti='Add to MyFshare'
	elif query=='Rename':
		data='{"token":"%s","new_name":"%s","file":"%s"}'%(token,new_name,id);noti='Rename in MyFshare'
	elif query=='Remove':data='{"token":"%s","items":["%s"]}'%(token,id);noti='Remove from MyFshare'
	elif query=='Upload':
		SESSID=hd['Cookie'].split('=')[1]
		name=re.sub('\[COLOR.{,12}\]|\[/COLOR\]|Fshare|4share|TenLua|List xml|-|:|"','',os.path.basename(url))
		path=xshare_group(re.search('data-id="%s" path-origin = "" data-path="(.+?)"'%myFshare,body),1)
		data='{"SESSID":"%s","name":"%s","size":"%s","path":"%s","token":"%s","secured":1}'%(SESSID,name,size,path,token)
		response=make_post(href,data,hd)
		if response and response.status==200:
			href=response.json['location'];data=content;noti='Upload to MyFshare'
		else:mess(u'Không lấy được link upload');return
	
	response=make_post(href,data,hd);logoutfshare(hd['Cookie'])
	if response and response.status==200:
		mess(u'%s thành công'%noti)
		if query!='Add' and query!='Upload':xbmc.executebuiltin("Container.Refresh");mess(u'Đang reload list')
	else:mess(u'%s không thành công'%noti)
	return

def make_favourites(name,url,img,fanart,mode,query):
	favourites=os.path.join(datapath,"favourites.xml")
	name=re.sub('\[COLOR.{,12}\]|\[/COLOR\]|Fshare|4share|TenLua|List xml|-|:|"','',name).strip()
	if query=='Add':
		if url.strip() in makerequest(favourites):mess(u'Mục này đã có trong MyFavourites');return
		if img==fanart:fanart=''
		string='<a href="%s" img="%s" fanart="%s">%s</a>\n'%(url.strip(),img,fanart,name)
		if makerequest(favourites,string=string,attr='a'):mess(u'Đã thêm 1 mục vào MyFavourites')
		else:mess(u'Thêm 1 mục vào xshare favourites thất bại')
	elif query=='Rename':
		title = get_input('Sửa tên trong mục MyFavourites',name).strip()
		if not title or title==name:return 'no'
		body=makerequest(favourites)
		string=re.search('((<a href="%s" img=".*?" fanart=".*?">).+?</a>)'%(url),body)
		if string:
			body=body.replace(xshare_group(string,1),xshare_group(string,2)+title+'</a>')
			if makerequest(favourites,string=body,attr='w'):
				mess(u'Đã sửa 1 mục trong MyFavourites')
				xbmc.executebuiltin("Container.Refresh")
			else:mess(u'Sửa 1 mục trong MyFavourites thất bại')
		else:mess(u'Sửa 1 mục trong MyFavourites thất bại')
	elif query=='Remove':
		body=makerequest(favourites)
		string=re.search('(<a href="%s" img=".*?" fanart=".*?">.+?</a>)'%(url),body)
		if string:
			body=body.replace(xshare_group(string,1)+'\n','')
			if makerequest(favourites,string=body,attr='w'):
				mess(u'Đã xóa 1 mục trong xshare favourites')
				xbmc.executebuiltin("Container.Refresh")
			else:mess(u'Xóa 1 mục trong xshare favourites thất bại')
		else:mess(u'Xóa 1 mục trong xshare favourites thất bại')
	else:
		items=re.findall('<a href="(.+?)" img="(.*?)" fanart="(.*?)">(.+?)</a>',makerequest(favourites))
		for href,img,fanart,name in items:addirs(name,href,img,fanart)
	return

def make_mylist(name,url,img,fanart,mode,query):
	mylist=os.path.join(thumuccucbo,'mylist.xml')
	name=re.sub('\[COLOR.{,12}\]|\[/COLOR\]|Fshare|4share|TenLua|List xml|-|:|"','',name).strip()
	if query=='Add':
		if url.strip() in makerequest(mylist):mess(u'Mục này đã có trong MyList');return
		if img==fanart:fanart=''
		string='<a href="%s" img="%s" fanart="%s">%s</a>\n'%(url.strip(),img,fanart,name)
		if makerequest(mylist,string=string,attr='a'):mess(u'Đã thêm 1 mục vào mylist.xml')
		else:mess(u'Thêm vào mylist.xml thất bại')
	elif query=='Rename':
		title = get_input('Sửa tên 1 mục trong mylist.xml',name)
		if not title or title==name:return 'no'
		string1='<a href="%s" img=".*?" fanart=".*?">.+?</a>'%url
		string2='<a href="%s" img=".*?" fanart=".*?">%s</a>'%(url,title)
		body=re.sub(string1,string2,makerequest(mylist))
		if makerequest(mylist,string=body,attr='w'):
			mess(u'Đã sửa 1 mục trong mylist.xml');xbmc.executebuiltin("Container.Refresh")
		else:mess(u'Sửa 1 mục trong mylist.xml thất bại')
	elif query=='Remove':
		string='<a href="%s" img=".*?" fanart=".*?">.+?</a>\n'%url
		body=re.sub(string,'',makerequest(mylist))
		if makerequest(mylist,string=body,attr='w'):
			mess(u'Đã xóa 1 mục trong mylist.xml');xbmc.executebuiltin("Container.Refresh")
		else:mess(u'Xóa 1 mục trong mylist.xml thất bại')
	return
	
def make_request(url,headers={'User-Agent':'Mozilla/5.0 Chrome/39.0.2171.71 Firefox/33.0'},json=0):
	try:
		response = urlfetch.get(url,headers=headers)
		if json:body=response.json
		else:body=response.body
		response.close()
	except: mess('Make Request Error: %s'%url);print 'Make Request Error: %s'%url;body=''
	return body#unicode:body=response.text

def make_post(url,data,headers):
	try:response=urlfetch.post(url=url,headers=hd,data=data, follow_redirects=False)
	except:mess(u'Không truy cập được %s'%url);response=''
	return response

def makerequest(file,string='',attr='r'):
	file=str2u(file)
	if attr=='r':
		try:f=open(file);body=f.read();f.close()
		except:mess(u'Lỗi đọc file: %s'%os.path.basename(file));body=''
	else:
		try:f=open(file,attr);f.write(string);f.close();body='ok'
		except:mess(u'Lỗi ghi file: %s'%os.path.basename(file));body=''
	return body

def download_subs(url):
	response=urlfetch.get(url)
	if int(response.getheaders()[0][1])<10485760:#size<10MB
		filename=no_accent(os.path.basename(url))
		filename=re.sub('\[.+?\]','',filename);f_fullpath=os.path.join(thumuccucbo,filename)
		if os.path.isfile(f_fullpath):
			try:os.remove(f_fullpath)
			except:mess(u'File đã có trong Thư mục riêng trên máy: %s'%filename);return
		try:
			f=open(f_fullpath,"wb");f.write(response.body);f.close()
			mess(u'Đã tải file %s vào Thư mục riêng trên máy'%filename)
		except:pass
	return

def get_input(title=u"", default=u""):
	result = ''
	keyboard = xbmc.Keyboard(default, title)
	keyboard.doModal()
	if keyboard.isConfirmed():
		result = keyboard.getText()
	return result

def tenlua_get_detail_and_starting(idf,h={'User-Agent':'xshare'}):
	data='[{"a":"filemanager_builddownload_getinfo","n":"%s","r":%s}]'%(idf,str(random.random()))
	try:
		response = urlfetch.post('https://api2.tenlua.vn/',data=data,headers=h,follow_redirects = False)
		body=response.json[0]
	except:body={'type':'none'}
	return body

def resolve_url(url,xml=False):
	if 'fshare.vn' in url.lower():hd['Cookie'] = loginfshare();srv='fshare.vn'
	elif '4share.vn' in url.lower():hd['Cookie'] = login4share();srv='4share.vn'
	elif 'tenlua.vn' in url.lower():
		hd['Cookie'] = logintenlua();srv='tenlua.vn'
		idf=xshare_group(re.search('\w{14,20}',url),0)
		if not idf:idf=url.split('/download/')[1].split('/')[0]
		download_info=tenlua_get_detail_and_starting(idf,hd)
		if 'n' in download_info and os.path.splitext(download_info['n'])[1][1:].lower() not in media_ext:
			mess('sorry! this is not a media file');return 'fail'
		if 'dlink' in download_info:url=download_info['dlink']
		elif 'url' in download_info:url=download_info['url'];mess(u'Slowly direct link!')
		else:mess(u'Không get được max speed link!');return 'fail'
	cookie = hd['Cookie']
	try:response=urlfetch.get(url, headers=hd, follow_redirects=False)
	except:mess(u'Không kết nối được server %s'%srv);xbmc.sleep(500);logout_site(cookie);return 'fail'
	if response.status==302:direct_link=response.headers['location']
	elif response.status==200 and 'fshare.vn' in url.lower():direct_link=resolve_url_fshare200(url,response,hd)
	elif response.status==200 and '4share.vn' in url.lower():
		FileDownload=re.search("<a href='(http://.{3,5}4share.vn.+?)'> <h4>(.+?)</h4>",response.body)
		if FileDownload:direct_link=xshare_group(FileDownload,1);srv=xshare_group(FileDownload,2)
		else:direct_link='fail'
	else:direct_link='fail'
	logout_site(cookie)
	if direct_link=='fail':
		if 'fshare.vn' not in url.lower():mess(u'Không get được max speed direct link!')
		return 'fail'
	if xml:return direct_link
	if not check_media_ext(direct_link,srv):return 'fail'
	xbmcsetResolvedUrl(direct_link);return ''

def check_media_ext(direct_link,srv):
	check=True;message='sorry! this is not a media file'
	sub_ext=['rar','zip','srt', 'sub', 'txt', 'smi', 'ssa', 'ass']
	if 'fshare.vn' in direct_link and os.path.splitext(direct_link)[1][1:].lower() not in media_ext:
		if os.path.splitext(direct_link)[1][1:].lower() in sub_ext:
			download_subs(direct_link)
		else:mess(message)
		check=False
	elif '4share.vn' in direct_link and os.path.splitext(srv)[1][1:].lower() not in media_ext:
		if os.path.splitext(srv)[1][1:].lower() in sub_ext:
			download_subs(direct_link)
		else:mess(message)
		check=False
	return check

def resolve_url_fshare200(url,response,hd):
	fs_csrf=xshare_group(re.search("fs_csrf: '(.+?)'",response.body),1)
	direct_link=get_direct_link_fshare200(fs_csrf,hd)
	if direct_link=='fail':
		temp=re.search('<span class="glyphicon glyphicon-remove"><.+b>(.+?)</b></h3>',response.body)
		if temp:mess(str2u(xshare_group(temp,1)));return 'fail'
		temp=re.search('<div class="alert alert-danger".+>[\s.*]{,3}(.+?)<a.+>(.+?)</a>',response.body)
		if temp:mess(str2u(xshare_group(temp,1)).strip().split('.')[0]);return 'fail'
		if re.search("form-control pwd_input",response.body):
			pw = get_input('Hãy nhập: Mật khẩu tập tin')
			if pw is None or pw=='':mess(u'Bạn đã không nhập password!');return 'fail'
			data={'fs_csrf':fs_csrf,'FilePwdForm[pwd]':pw};response=make_post(url,data,hd)
			if response:
				try:
					if response.status==302:direct_link=response.headers['location']
					elif response.status==200:direct_link=get_direct_link_fshare200(fs_csrf,hd)
					else:direct_link='fail'
				except:direct_link='fail';print 'Fshare not response direct_link'
			else:f=''
	return direct_link

def get_direct_link_fshare200(fs_csrf,hd):
	data=urllib.urlencode({'speed':'fast','fs_csrf':fs_csrf})
	response=make_post('https://www.fshare.vn/download/index',data,hd)
	if response:
		try:direct_link=response.json['url'].encode('utf-8')
		except:direct_link='fail';print 'Fshare response status 200 and not json["url"]'
	else:direct_link='fail'
	return direct_link
	
def logout_site(cookie):
	if cookie and myaddon.getSetting('logoutf')=="true":
		if 'fshare.vn' in url.lower():logoutfshare(cookie)
		elif '4share.vn' in url.lower():logout4share(cookie)
		elif 'tenlua.vn' in url.lower():logouttenlua(cookie)
	
def loginfshare():
	url = "https://www.fshare.vn/login"
	try:
		response = urlfetch.get(url,headers=hd)
		body=response.body;hd['Cookie']=response.cookiestring;response.close()
		fs_csrf=xshare_group(re.search('value="(.+?)".*name="fs_csrf',body),1)
		form_fields = {
			"LoginForm[email]": myaddon.getSetting('usernamef'), 
			"LoginForm[password]": myaddon.getSetting('passwordf'),"LoginForm[rememberMe]": "0",
			"fs_csrf":fs_csrf}
		data=urllib.urlencode(form_fields);response=make_post(url,data,hd)
		if response and response.status==302:mess(u'Login Fshare.vn thành công',timeShown=100);f=response.cookiestring
		else:mess(u'Login Fshare.vn không thành công');f=''
	except:mess(u'Lỗi Login Fshare.vn');f=''
	return f

def logoutfshare(cookie):
	hd['Cookie'] = cookie
	try:
		urlfetch.get("https://www.fshare.vn/logout",headers=hd,follow_redirects=False)
		mess(u'Logout Fshare.vn thành công')
	except:mess(u'Logout Fshare.vn không thành công')
	
def login4share():
	url = 'http://up.4share.vn/index/login'
	form_fields = {"username":myaddon.getSetting('username4'),"password":myaddon.getSetting('password4')}
	data=urllib.urlencode(form_fields);response=make_post(url,data,hd)
	if response and response.status==302:mess(u'Login 4share.vn thành công',timeShown=100);f=response.cookiestring
	else:mess(u'Login 4share.vn không thành công');f=''
	return f

def logout4share(cookie):
	hd['Cookie'] = cookie
	try:
		urlfetch.get("http://up.4share.vn/index/logout",headers=hd,follow_redirects=False)
		mess(u'Logout 4share.vn thành công')
	except:mess(u"Logout 4share.vn không thành công")
	
def logintenlua():
	url = 'https://api2.tenlua.vn/';user=myaddon.getSetting('usernamet');pw=myaddon.getSetting('passwordt')
	data='[{"a":"user_login","user":"'+user+'","password":"'+pw+'","permanent":"true"}]'
	response=make_post(url,data,hd)
	if response and response.body!='[-1]':mess(u'Login tenlua.vn thành công');f=response.headers.get('set-cookie')
	else:mess(u'Login tenlua.vn không thành công');f=''
	return f
	
def logouttenlua(cookie):
	hd['Cookie']=cookie;data=urllib.urlencode({"a":"user_logout"})
	response=make_post('https://api2.tenlua.vn/',data,hd)
	if response:mess(u'Logout tenlua.vn thành công')
	else:mess(u"Logout tenlua.vn không thành công")
	
def loginhdvietnam():
	url='http://www.hdvietnam.com/diendan/login.php';hd={'User-Agent':'Mozilla/5.0 Chrome/39.0.2171.71 Firefox/33.0'}
	user=myaddon.getSetting('usernameh');pw=myaddon.getSetting('passwordh')
	form_fields ={"vb_login_username":user,"vb_login_password":pw,"do":"login"}
	data=urllib.urlencode(form_fields);response=make_post(url,data,hd)
	if response and 'vbseo_loggedin=yes' in response.cookiestring:
		f=response.cookiestring
		mess(u'Login hdvietnam.com thành công',timeShown=100);myaddon.setSetting('cookie',f)
	else:mess(u'Login hdvietnam.com không thành công');f=''
	return f

def logindangcaphd():
	url="http://dangcaphd.com/login.html";hd['Cookie']=''
	#Vì đang trong quá trình thử nghiệm, xin các bạn đừng đổi pass acc nhé. Cảm ơn!
	if 'xshare' in myaddon.getSetting('mail_dchd'):
		p=xshare_group(re.search('Email:(.+?)</p>',make_request('http://dangcaphd.com/contact.html')),1).strip()
	else:p=myaddon.getSetting('pass_dchd')
	form_fields={"_submit":"true","email": myaddon.getSetting('mail_dchd'),"password": p}
	data=urllib.urlencode(form_fields);response=make_post(url,data,hd)
	if response:
		if 'complete' in response.json:
			f=response.cookiestring;myaddon.setSetting('cookie',f)
			mess(u'Login dangcaphd.com thành công',timeShown=100)
		else:mess(u'Login dangcaphd.com không thành công');f=''
	else:f=''
	return f

def logoutdangcaphd(cookie):
	hd['Cookie'] = cookie
	try:
		urlfetch.get("http://dangcaphd.com/logout.html",headers=hd,follow_redirects=False)
		mess(u'Logout dangcaphd.com thành công',timeShown=100)
	except:mess(u'Logout dangcaphd.com không thành công')
	
def trangtiep(query,items):
	if 'Trang' in query.split('?')[0]:
		trang=int(query.split('?')[0].split('Trang')[1])
		query=query.split('?')[1]
	else:trang=1
	del items[0:(trang-1)*rows]
	trang+=1
	return trang,query,items
	
def hdvn_get_link(url,fanart='',temp=[]):
	if 'chuyenlink.php' in url or 'print.html' in url:return temp
	hd['Cookie']=myaddon.getSetting('cookie')
	body=make_request(url,headers=hd)
	bossroom=hdvn_boss_room(body)
	if myaddon.getSetting('hdvnfindall')=='false':
		uploaders=myaddon.getSetting('uploaders').lower().split('-')
		if bossroom not in uploaders:return temp
	if 'post_thanks_separator' not in body and myaddon.getSetting('usernameh') not in body:
		hd['Cookie']=loginhdvietnam()
		body=make_request(url,headers=hd)
	if not body:return temp

	title=xshare_group(re.search('<title>(.+?)</title>',body),1)
	if not title:return temp
	else:title=re.sub('\||\[.*\]|\(.*\)|\{.*\}|amp;','',title).strip()
	title='[%s] '%bossroom+title;mess(url.split('/')[len(url.split('/'))-1],100)

	img=xshare_group(re.search('<a rel="nofollow" href="(.+?)" class="highslide"',body),1)
	if not fanart:fanart=img
	pattern_link='(https?://www.fshare.vn/\w{4,6}/\w{10,14})'
	pattern_link+='|(http://4share.vn/./\w{14,20})|(https?://w?w?w?/?tenlua.vn/.*?)[ |"|<]'
	pattern_link+='|(http://subscene.com/subtitles/.+?)[ |"|\'|<]'
	items=re.findall(pattern_link,hdvn_body_thanked(url,body,hd))
	boss=img=''
	for hrefs in items:
		for href in hrefs:
			if not href:continue
			href=correct_link(href)
			if not href or href in temp:continue
			temp.append(href);addirs(title,href,img,fanart)
	return temp
	
def hdvn_boss_room(content):
	r='class="username o..?line popupctrl" href="http://www.hdvietnam.com/diendan/members/\d{,7}-(.+?).html"'
	bossroom=xshare_group(re.search(r,content),1)
	if not bossroom:bossroom='Unknown'
	return bossroom
	
def hdvn_body_thanked(url,body,hd):
	thanks_links=[]
	for id_post in re.findall('id="post_(\d{5,7})"',body):
		for thanks_link in re.findall('<a href="(.+p=%s.{,8}securitytoken=.+)" id'%id_post,body):
			thanks_link=re.sub('amp;','',thanks_link)
			urlfetch.get(thanks_link,headers=hd)
			thanks_links.append(re.sub('post_thanks_add','post_thanks_remove_user',thanks_link))
	body=make_request(url,headers=hd)
	for thanks_link in thanks_links:temp=make_request(re.sub('&securitytoken.+','',thanks_link),headers=hd)
	return body 

def google_ifile(url,name,temp=[]):
	if 'http://ifile.tv/phim/' not in url:return temp
	mess(url,100)
	for url4share,fanart,name2,catalog in ifile_tv_4share(url):
		if not name2:name2=name
		if url4share not in temp:temp.append(url4share);addirs(name2,url4share,fanart,fanart)
	return temp

def google_vaphim(url,temp=[]):
	if url=='http://vaphim.com/':return temp
	elif '/tag/' in url:
		pattern='class="entry-title"><a href="(.+?)" rel="bookmark"'
		url=xshare_group(re.search(pattern,make_request(url)),1)
		if not url:return temp
	mess(url,100)
	for img,fanart,href,name in vp2fshare(url):
		if href not in temp:temp.append(href);addirs(name,href,img,fanart)
	return temp

def google_search_api(url,start,string,items):#url:fshare.vn,4share.vn,tenlua.vn,hdvietnam.com
	string_search = urllib.quote_plus('"%s"'%string)
	href = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=large&'
	href+='start=%s&q=site:%s+%s'%(start,url.lower(),string_search)
	json=make_request(href,json=1)
	if not json:mess(u'Lỗi get %s'%href);return items,'end'
	if json['responseStatus']==403:
		mess(u'Google: nghi ngờ lạm dụng Dịch vụ. Tự động chuyển sang web search')
		return google_search_web(url,query,page,mode,items)
	data=json['responseData']
	if not data or not data['results']:mess(u'Không tìm được tên phim phù hợp');return items,'end'
	currentPage=int(data['cursor']['currentPageIndex'])+1;nextPage=0
	for i in data['results']:
		if 'tenlua' in url and re.search('\w{16,20}/(.*)\Z',i['url'].encode('utf-8')):
			name=xshare_group(re.search('\w{16,20}/(.*)\Z',i['url'].encode('utf-8')),1)
		else: name=i['titleNoFormatting'].encode('utf-8')
		name=re.sub('\||<.+?>|\[.*\]|\(.*\)','',name.split(':')[0]).strip()
		if name and 'Forum' not in name and 'server-nuoc-ngoai' not in i['url']:
			items.append((name,i['url'].encode('utf-8')))
	start=str(int(start)+8)
	if start not in ' '.join(s['start'] for s in data['cursor']['pages']):start='end'
	return items,start

def google_search(url,query,mode,page,items=[]):
	srv=url.split('.')[0]
	if page==0:get_file_search(url,mode)
	elif page==1:
		query=get_string_search(url)
		if query:return google_search(url,query,mode,page=4)
		else:return 'no'
	else:
		query=no_accent(query);tempurl=[];templink=[]
		if '?' in query:
			start=query.split('?')[1];query=query.split('?')[0]
		else:start='0'
		if googlesearch=='Web':items,start=google_search_web(url,start,query,items)
		else:items,start=google_search_api(url,start,query,items)
		if not items:return 'no'
		for name,link in sorted(items,key=lambda l:l[0]):
			if link in templink:continue
			if url=='hdvietnam.com':tempurl=hdvn_get_link(link,temp=tempurl)
			elif url=='vaphim.com':tempurl=google_vaphim(link,temp=tempurl)
			elif url=='ifile.tv':tempurl=google_ifile(link,name,temp=tempurl)
			elif url=='4share.vn' and 'docs.4share' not in link:tempurl=doc_Trang4share(link,temp=tempurl)
			else:addirs(name,link,icon[srv])
			templink.append(link)
		if start!='end':
			name=color['trangtiep']+'Trang tiep theo...trang %s[/COLOR]'%str(page-2)
			addir(name,url,icon[srv],mode=mode,query='%s?%s'%(query,start),page=page+1,isFolder=True)
	return ''
  
def google_search_web(url,start,query,items):
	num='20';google = 'https://www.google.com.vn/search?hl=vi&ie=utf-8&oe=utf-8&num=%s&'%num
	string_search = urllib.quote_plus('"%s"'%query);srv=url.split('.')[0]
	href=google+'start=%s&q=site:%s+%s'%(start,url.lower(),string_search)
	body=make_request(href)
	if '<TITLE>302 Moved</TITLE>' in body:
		mess(u'Google từ chối dịch vụ do bạn đã truy cập quá nhiều');return items,'end'
	links=re.findall('<a href="(.{,300})" onmousedown=".{,200}">(.{,200})</a></h3>',body)
	for link,name in links:items.append((name,link))
	start=str(int(start)+int(num))
	if 'start=%s'%start not in body:start='end'
	return items,start

def open_category(query): #category.xml
	pattern='<a server="(...)" category="(.+?)" mode="(..)" color="(.*?)" icon="(.*?)">(.+?)</a>'
	items=re.findall(pattern,makerequest(os.path.join(data_path,'category.xml')))
	for server,category,mode,colo,icon,name in items:
		if (server!=query) or (("18" in category) and (phim18=="false")):continue
		if query=='VPH' and mode!='10':q='vaphim.xml'
		elif query=='IFI' and mode!='10':q='ifiletv.xml'
		else:q=category
		name='[COLOR '+colo+']'+name+'[/COLOR]';icon=icon_path+icon
		addir(name,category,icon,home+'/fanart.jpg',mode=int(mode),page=0,query=q,isFolder=(mode!='16'))

def main_menu(category,page,mode,query): #Doc list tu vaphim.xml hoac ifiletv.xml
	items = doc_xml(os.path.join(datapath,query),para=category);pages=len(items)/rows+1
	del items[0:page*rows];count=0;down=len(items)
	for id,img,fanart,href,name in items:
		down-=1;addirs(name,href,img,fanart);count+=1
		if count>rows and down>10:break
	if down>10:
		page+=1;name=color['trangtiep']+'Trang tiep theo...trang %d/%d[/COLOR]'%(page+1,pages)
		addir(name,category,icon['icon'],mode=mode,page=page,query=query,isFolder=True)
	
def update_xml(items_new,items_old,filename): #update vaphim,ifiletv xml
	try:items = sorted(items_new+items_old,key=lambda l:int(l[1]),reverse=True)
	except:items = items_new+items_old
	content='<?xml version="1.0" encoding="utf-8">\n'
	for id_tip,id_htm,category,img,fanart,href,fullname in items:
		content+='<a id_tip="%s" id="%s" category="%s" img="%s" fanart="%s" href="%s">%s</a>\n'%(id_tip,id_htm,category,img,fanart,href,fullname)
	if makerequest(os.path.join(datapath,filename),string=content,attr='w'):
		mess(u"Đã cập nhật được %d phim"%len(items_new))
	else: mess(u'Đã xảy ra lỗi cập nhật')
	return

def vp_update():
	items_old, id_old = read_items_old("vaphim.xml")
	mess(u'Đang kiểm tra dữ liệu cập nhật của Vaphim...')

	new_items = vaphim_page('http://vaphim.com/category/phim-2/');items_new=[];str_items_old=str(items_old)
	for id_tip,id_htm,category,href in new_items:
		if id_htm not in id_old:
			try:
				for img,fanart,href,fullname in vp2fshare(href): # vp2fshare:img,fanart,href,fullname
					if href not in str_items_old:
						fullname=' '.join(s for s in fullname.split())
						items_new.append((id_tip,id_htm,category,img,fanart,href,fullname))
			except:continue
	if items_new:update_xml(items_new,items_old,"vaphim.xml")
	else:mess(u'Không có phim mới...')
	return 'ok'

def data_download():
	check=True;p=datapath
	if not os.path.isfile(os.path.join(p,"vaphim.xml")) or os.path.getsize(os.path.join(p,"vaphim.xml"))<4317000:
		mess(u'Đang download danh mục Vaphim.com, ifile.tv,...');data1='data-3.2.0.zip';data2='data_hot-3.2.0.zip'
		for filename in os.listdir(datapath):
			if '.' in filename:
				try:os.remove(os.path.join(datapath, filename))
				except:mess(u'Download data cho xshare không thành công!');return False
		pattern='href="(.+?)" title="%s"'%data1
		data=xshare_group(re.search(pattern,urlfetch.get('https://www.fshare.vn/folder/GZCI8AHAQJ75').body),1)
		url=resolve_url(data.replace('http:','https:'),True)
		if url=='fail':
			pattern='href="(.+?)" title="%s"'%data2
			data=xshare_group(re.search(pattern,urlfetch.get('https://www.fshare.vn/folder/GZCI8AHAQJ75').body),1)
			try:
				response=urlfetch.get(data.replace('http:','https:'), headers=hd, follow_redirects=False)
				if response.status==302:url=response.headers['location']
				else:check=False
			except:check=False
		if check:
			try:
				body=urlfetch.get(url).body
				tempfile = os.path.join(datapath, "xshare-data.zip")
				f = open(tempfile, "wb");f.write(body);f.close()
				xbmc.sleep(500)
				xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (tempfile, datapath,)), True)
			except:check=False
		if check:mess(u'Download data cho xshare thành công!')
		else:mess(u'Download data cho xshare không thành công!')
	return check

def vp_update_rss():
	items=rss_content('http://feed.vaphim.com/category/phim-2/feed/')
	id_old=re.findall('id="(\d{5})" category',makerequest(os.path.join(datapath,"vaphim.xml")))
	category={'Phim Lẻ':'phim-le','Phim Bộ':'series','Phim Bộ Hàn':'korean-series','Phim Bộ Hồng Kông':'hongkong-series','Phim Bộ Mỹ':'us-tv-series','Phim Tài Liệu':'documentary','Phim 18+':'18','Hoạt Hình':'animation','Huyền Bí':'mystery','Viễn Tưởng':'sci-fi','3D':'3d','Cao Bồi':'western','Chiến Tranh':'war','Thiếu Nhi':'family','Hài Hước':'comedy','Hành Động':'action','Hình Sự':'crime','Rùng Rợn':'thriller','Tâm Lý':'drama','TVB':'tvb','Kinh Dị':'horror','Lãng Mạn':'romance','Lịch Sử':'history','Phiêu Lưu':'adventure','Thần Thoại':'fantasy','Thuyết Minh':'thuyet-minh-tieng-viet','Hồng Kông':'hongkong','Ấn Độ':'india','Việt Nam':'vietnamese','Hàn Quốc':'korean'}
	content_new=''
	pattern='(https?://www.fshare.vn/\w{4,6}/\w{10,14})" target="_blank">(.+?)</a>'
	for item in items:
		cate=''
		for i in item.findall('category'):
			if i.text.encode('utf-8') in category:
				cate+=category[i.text.encode('utf-8')]+' '
			else:break
		cate=cate.strip()
		idf=xshare_group(re.search('(\d{5})',item.findtext('guid')),1)
		if not idf or not cate or idf in id_old:continue
		
		name=item.findtext('title')
		content=item.findtext('contentencoded')
		img=re.findall('img src="(.+?jpg)["|?| ]',content)
		if len(img)>1:fanart=img[1];img=re.sub('-134x193','',img[0])
		elif len(img)>0:fanart=img=re.sub('-134x193','',img[0])
		else:fanart=img=''
		
		for link,title in re.findall(pattern,content):
			link=link.lower();idp=xshare_group(re.search('(\w{10,14})',link),1)
			if 'fshare.vn/file' in link:url='https://www.fshare.vn/file/%s'%idp.upper()
			else:url='https://www.fshare.vn/folder/%s'%idp.upper()
			content_new+='<a id_tip="" id="%s" category="%s" img="%s" fanart="%s" href="%s">%s</a>\n'%(idf,cate,img,fanart,url,name+' - '+title)
	if content_new:
		makerequest(os.path.join(datapath,"vaphim.xml"),string=content_new.encode('utf-8'),attr='a')

def vaphim_page(url):
	body=make_request(url);items_new=[]
	if str('<h2>Search Results</h2>') in body:return []
	items=re.findall('<li class="post-(.+?)">\s*.*\s*<a data="(\d{,6})" title=.+href="(.+?)">',body)
	for category,ID,href in items:
		if ('game' not in category) and ('video' not in category) and ('phn-mm' not in category):
			category=' '.join([s[s.find('-')+1:] for s in category.rsplit(' ') if 'category' in s])
			items_new.append(('',ID,category,href))
	return items_new #vaphim_page1(url):'',ID,category,href

def clean_string(string):
	return ' '.join(s for s in re.sub('Fshare|-|4share|Tenlua|&.+ ','',string).split())

def vp2fshare(url):
	body = make_request(url);combs=[]
	category=xshare_group(re.search('<div id="post-(\d{,6})".*\s.*</strong><a(.*?)\d{,5}</div>',body),2)
	if not re.search('"http://vaphim.com/category/.{,8}[i|v].{,4}/.{,20}"',category):return combs
	if '<p><strong>' in body:#tuyen tap
		pattern='<strong>(.+?)</strong>|src="(.+)\?.{,10}"|(https?://www.fshare.vn/\w{4,6}/\w{10,14}).{,20}>(.+?)</a>'
		pattern+='|"(http://subscene.com/subtitles/.+?)"'
		body=body[body.find('<p><strong>'):]
		while '<div class="cf5_wpts_cl">' in body:
			temp=body[:body.find('<div class="cf5_wpts_cl">')]
			body=body[len(temp)+len('<div class="cf5_wpts_cl">'):]
			items=re.findall(pattern,temp)
			if len(items)>2:#ton tai link fshare
				if items[0][0]:title=re.sub('&#.* ','',items[0][0]).strip()+' - '
				else:title=''
				if items[1][1]:img=fanart=items[1][1]
				else:img=fanart=''
				nname=''
				for n,i,href,name,subs in items:
					if "fshare.vn" in href:combs.append((img,fanart,href.replace('http:','https:'),title+name))
					elif "subscene.com" in subs:combs.append((img,fanart,subs,title+nname))
					nname=name
	else:
		pattern='<title>(.+?)</title>|<meta itemprop="name" .?content="(.+?)"'
		pattern+='|<meta itemprop="image" .?content="(.+?)"|<div id="attachment.*"><img src="(.+?\.jpg).{,10}" '
		pattern+='|<img src="(.+jpg).{,10}".{,100}size-full'
		pattern+='|(https?://www.fshare.vn/\w{4,6}/\w{10,14}).{,20}>(.+?)</a>|"(http://subscene.com/subtitles/.+?)"'
		items=re.findall(pattern,body)
		if len(items)>4:#ton tai link fshare
			if items[1][1]:title=items[1][1]+' - '
			elif items[0][0]:title=items[0][0]+' - '
			else:title=''
			if items[2][2]:img=fanart=re.sub('-\d{,4}x\d{,5}','',items[2][2])
			elif items[3][3]:img=fanart=re.sub('-\d{,4}x\d{,5}','',items[3][3])
			else:img=fanart=''
			if items[4][4]:fanart=items[4][4]
			nname=''
			for t,n,i,f,im,href,name,subs in items:
				if "fshare.vn" in href:combs.append((img,fanart,href.replace('http:','https:'),title+name))
				elif "subscene.com" in subs:combs.append((img,fanart,subs,title+nname))
				nname=name
	return combs #(img,fanart,href,fullname)

def vp_xemnhieu():
	body=urlfetch.get('http://vaphim.com/request/').body
	url_new = re.findall('<li><a href="(http://vaphim.com.+?)"',body);list_new=[];ghifile=False
	body = makerequest(os.path.join(data_path,"vp_xemnhieu.xml"))
	url_old = re.findall('<a url="(.+?)"',body)
	content='<?xml version="1.0" encoding="utf-8" mode="91">\n'
	for url in url_new:
		if url not in url_old: #vp2fshare(url):img,fanart,href,fullname
			items=vp2fshare(url)
			if items:ghifile=True
		else:
			items=re.findall('<a url="%s" img="(.*?)" fanart="(.*?)" href="(.+?)">(.+?)</a>'%url,body)
		for img,fanart,href,name in items:
			addirs(re.sub('&.* ','',name),href,img,fanart,url)
			content+='<a url="%s" img="%s" fanart="%s" href="%s">%s</a>\n'%(url,img,fanart,href,name)
	if ghifile:makerequest(os.path.join(data_path,"vp_xemnhieu.xml"),string=content,attr='w')

def daklak47(name,url,img):
	reps = urlfetch.get(url)
	if reps.status==302:
		req=reps.headers['location']
		url = req.replace('http:','https:')
		if 'www.fshare.vn/folder/' in url:mess(u"Chưa xử lý trường hợp đọc folder trên 47daklak.com");return
		else:resolve_url(url)
	else: mess("Khong tim thay link tren "+url)

def phimchon(url,filename,re_string):
	if "index" in url:
		data = urllib.urlencode({'type':'special_filter','filter_by_view_desc':'1'})
		fetch = urlfetch.fetch(url+"/filter",method='POST',headers=hd,data=data,follow_redirects=False)
		hd['Cookie']=fetch.headers.get('set-cookie')
	id_new = re.compile(re_string).findall(urlfetch.fetch(url).body)
	items_old, id_old = read_items_old(filename);items_new=[]
	for ID in id_new:
		try:
			i = id_old.index(ID)
			while id_old[i] == ID:	
				addirs(items_old[i][6],items_old[i][5],items_old[i][3],items_old[i][4])
				i+=1
		except:continue

def doc_list_xml(url,filename='',page=0):
	if not page:
		items=doc_xml(url,filename=filename)
		makerequest(os.path.join(data_path,'temp.txt'),string=str(items),attr='w')
	else:f=open(os.path.join(data_path,'temp.txt'));items=eval(f.readlines()[0]);f.close()
	pages=len(items)/rows+1
	del items[0:page*rows];count=0
	for id,href,img,fanart,name in items:
		if '47daklak.com' in href: addir(name,href,img,mode=47)
		else: addirs(name,href,img,fanart)
		count+=1
		if count>rows and len(items)>(rows+10):break
	if len(items)>(rows+10):
		page+=1;name=color['trangtiep']+'Trang tiep theo...trang %d/%d[/COLOR]'%(page+1,pages)
		addir(name,url,icon_path+'khophim.png',mode=97,page=page,isFolder=True)

def doc_xml(url,filename='',para=''): 
	if (datapath in url) or (thumuccucbo in url):body=makerequest(url)
	else:body=make_request(resolve_url(url,xml=True))

	if ('vaphim' in url) or ('ifiletv' in url) or ('phimfshare' in url) or ('hdvietnam' in url):
		if para and para[:6]=='search':
			if ('phimfshare' in url) or ('hdvietnam' in url):
				r='href="(.+?)" img="(.+?)">(.*%s.*)</a>'%para[7:];items=[]
				for href,img,name in re.compile(r, re.I).findall(no_accent(body)):
					items.append((img,img,href,name))
			else:
				r='img="(.*?)" fanart="(.*?)" href="(.+?)">(.*%s.*)</a>'%para[7:]
				items=re.compile(r, re.I).findall(no_accent(body))
		else:
			if not para:r='<a id_tip="(.*?)" id="(.+?)" category="(.*?)" img="(.*?)" fanart="(.*?)" href="(.+?)">(.+?)</a>'
			elif para=='post1': r='id="(.+?)"'
			else: #Doc theo category
				r='<a.*id="(.+?)" category=".*%s.*" img="(.*?)" fanart="(.*?)" href="(.+?)">(.+?)</a>'%para
			items = sorted(re.findall(r,body),key=lambda l:l[0], reverse=True)
	else:#Doc cac list xml khac
		r='<a.+id="(.*?)".+href="(.+?)".+img="(.*?)".+fanart="(.*?)".*>(.+?)</a>'
		items = re.compile(r).findall(body)
		if len(items)<1:items = re.findall('.+()href="(.+?)".+img="(.*?)".*()>(.+?)</a>',body)
		if len(items)<1:items = re.findall('.+()href="(.+?)".*()()>(.+?)</a>',body)
		if (copyxml=="true") and ('http' in url) and (len(items)>0) :
			filename=re.sub('\.xml.*','.xml',filename.replace('[COLOR orange]List xml[/COLOR]-',''))
			filename=re.sub('\[.{1,10}\]','',filename);f_fullpath=os.path.join(thumuccucbo,filename)
			if not os.path.isfile(f_fullpath):
				string='<?xml version="1.0" encoding="utf-8">\n'
				for id,href,img,fanart,name in items:
					string+='<a id="%s" href="%s" img="%s" fanart="%s">%s</a>\n'%(id,href,img,fanart,name)
				if makerequest(f_fullpath,string=string,attr='w'):
					mess(u'Đã ghi file %s vào Thư mục riêng trên máy'%filename)
	return items

def doc_TrangFshare(url,img,fanart,query=''):
	pageIndex=filescount=rowscount=files_count=0
	if 'pageIndex' in url:
		pageIndex=int(url.split('?')[1].split('=')[1]);filescount=int(url.split('?')[2].split('=')[1])
		rowscount=int(url.split('?')[3].split('=')[1])
	body = make_request(url);name=xshare_group(re.search('<title>(.+?)</title>',body),1)
	if not name:name='No name'
	if no_accent(name)=='Loi 404':mess(u'file/folder đã bị xóa');return 'no'
	else:name=re.sub('Fshare - ','',name)
	name_return=name
	if '/file/' in url:
		size=xshare_group(re.search('width="29".*\s.*<td>(.+?)</td>',body),1)
		items=[('',url,name,size,'')]
	else:
		files_count=xshare_group(re.search('Số lượng:(.+?)</div>',body),1)
		if files_count:files_count=int(files_count)
		else:files_count=filescount
		if files_count==0:mess(u'Thư mục trống');return 'no'
		pattern='data-id="(.+?)" .+? href="(.+?)".+title="(.+?)".*\s.*\s.*\s.*<.+?>(.+?)</div>.*\s.*<.+?>(.+?)</div>'
		items=re.findall(pattern,body)
		#items=re.findall('data-id="(.+?)" .+? href="(.+?)".+title="(.+?)"[\W\w]{,500}size align-right">(.+?)</div>',body)
		if url.strip()==thumucrieng and items:
			items=sorted(items,key=lambda l:(l[4][6:]+l[4][3:5]+l[4][:2]), reverse=True)
	for id,href,name,size,date in items:
		if re.search('/folder/\w{10,14}\?p=',href): #Thu muc con
			temp=xshare_group(re.search('(\w{10,14} )',name),1)
			if temp:id=temp
			href=check_id_fshare(id)
			name=re.sub('\w{10,14} ','',name)
		if url.strip()==thumucrieng:query='thumucrieng'
		if 'www.fshare.vn/file' in href:
			if name.strip()[-3:].lower()=='xml':query+='xml'
			#elif name.strip()[-3:].lower()=='m3u':
			elif len(size.strip())>2:name=name+" - "+size
		addirs(name,href.replace('http:','https:'),img,fanart,query)
	rowscount+=len(items)
	if ('/folder/' in url) and (rowscount<files_count):
		files_count=str(files_count);rowscount=str(rowscount);page=str(pageIndex+2);pageIndex=str(pageIndex+1)
		url=url.split('?')[0]+'?pageIndex=%s?files_count=%s?rows_count=%s'%(pageIndex,files_count,rowscount)
		name=color['trangtiep']+'Trang tiep theo...trang %s[/COLOR]'%page
		addir(name,url,img,fanart,mode=90,query=query,isFolder=True)
	return name_return

def doc_Trang4share(url,temp=[]):#38
	if '4share.vn/d/' in url:
		response=make_request(url)
		pattern="<a href='(.+?)' target='.+?'><image src = '.+?'>(.+?)<.*?><td style='text-align: right'>(.+?)</td>"
		pattern+="|<a href='(.+?)'>.*\s.*<image src = '.+?'>(.+?)</a></div>"
		for href,name,size,folder_link,folder_name in re.findall(pattern,response):
			if href:name=name.strip()+' - '+size.strip();href='http://4share.vn'+href
			else:href='http://4share.vn'+folder_link;name=folder_name.strip()
			if href not in temp:temp.append((href));addirs(name,href)
	elif '4share.vn/f/' in url:
		name_size=re.search('Filename:.{,10}>(.+?)</strong>.{,20}>(.+?)</strong>',make_request(url))
		if name_size:
			name=xshare_group(name_size,1)+' - '+xshare_group(name_size,2)
			if url not in temp:temp.append((url));addirs(name,url)
	return temp

def doc_thumuccucbo(name,url,img,fanart,mode,query):
	if url=='thumuccucbo':url=thumuccucbo
	url=str2u(url)
	if query=='Remove':
		if os.path.isfile(url):
			try:os.remove(url);mess(u'Đã xóa file: %s'%url);xbmc.executebuiltin("Container.Refresh")
			except:mess(u'Lỗi xóa file')
		else:
			import shutil
			try:shutil.rmtree(url);mess(u'Đã xóa thư mục: %s'%url);xbmc.executebuiltin("Container.Refresh")
			except:mess(u'Lỗi xóa thư mục')
	elif query=='Rename':
		name=str2u(os.path.basename(url))
		name_new = get_input('xshare - Rename file/folder (chú ý phần mở rộng)',name)
		if name_new and name_new!=name:
			try:
				os.rename(url,os.path.join(os.path.dirname(url),str2u(name_new)))
				mess(u'Đã đổi tên file/folder: %s'%url)
				xbmc.executebuiltin("Container.Refresh")
			except:mess(u'Lỗi Rename file/folder')
	elif thumuccucbo in url and query!='file':
		try:url=unicode(url,'utf8')
		except:url=str2u(url)
		for dirname,dirnames,filenames in os.walk(url):
			if dirname==url:
				for filename in filenames:
					filenamefullpath = os.path.join(dirname, filename)
					if os.path.isfile(filenamefullpath):
						filename=filename.encode('utf-8');filenamefullpath=filenamefullpath.encode('utf-8')
						file_ext=os.path.splitext(filenamefullpath)[1][1:].lower()
						if file_ext in media_ext:
							item = xbmcgui.ListItem(filename, iconImage=icon['khophim'])
							query=menuContext(filename,filenamefullpath,'','',mode,query,item)
							xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=filenamefullpath,listitem=item)
						elif file_ext=='xml':addirs(filename,filenamefullpath,icon['khophim'],query='xml')
						else:addirs(filename,filenamefullpath,query='file')
			else:
				dirname=dirname.encode('utf-8')
				name='%sThư mục %s[/COLOR]'%(color['trangtiep'],dirname)
				addir(name,dirname,img=icon['icon'],mode=mode,query=dirname,isFolder=True)
		return
	else:mess(u'Chưa xử lý kiểu file này')
	return 'no'

def play_maxspeed_link(): 
	query = get_input('Hãy nhập max speed link của Fshare, 4share hoặc tênlửa')
	if query is None or query=='':return 'no'
	query = query.replace(' ','')
	if len(query)<50:mess(u'Bạn nhập link ID chưa đúng: '+query);return 'no'
	xbmcsetResolvedUrl(query)
	return ''

def lay_link_tenlua(href):
	idf=xshare_group(re.search('\w{14,20}',href),0)
	if not idf:return
	response=tenlua_get_detail_and_starting(idf)
	if response["type"]=="file":
		name=response['n'].encode('utf-8');url="https://www.tenlua.vn/download/"+idf
		addir(name,url,mode=3)
	elif response["type"]=="folder":
		for item in response['content']:
			lay_link_tenlua(item['link'])
	
def check_id_fshare(id):
	id=id.upper()
	if re.search('download_folder',urlfetch.get('https://www.fshare.vn/folder/'+id).body):
		url='https://www.fshare.vn/folder/'+id
	elif re.search('pull-right file_info',urlfetch.get('https://www.fshare.vn/file/'+id).body):
		url='https://www.fshare.vn/file/'+id
	else:url=''
	return url

def check_id_4share(id):
	url='http://4share.vn/f/%s/'%id;name=''
	item=re.search('<center>.+?<strong>(.+?)</strong>.+?<strong>(.+?)</strong></center>',make_request(url))
	if item:name=xshare_group(item,1)+' - '+xshare_group(item,2)
	else:
		url='http://4share.vn/d/%s/'%id
		items=re.findall("<br/><b>(.+?)</b>|<a href='(/f/\w+)|<a href='(/d/\w+)'>",make_request(url))
		if len(items)>1:name=items[0][0]
	return name,url

def check_id_tenlua(id):
	response=tenlua_get_detail_and_starting(id);name=url=''
	if response["type"]=="file":name=response['n'];url="https://www.tenlua.vn/download/"+id
	elif response["type"]=="folder":name=response["folder_name"];url="https://www.tenlua.vn/fm/folder/"+id
	return name,url

def id_2url(url,name='',mode=0,page=0,query=''):
	print query,page
	if query=='Myshare':query=thumucrieng;page=4
	if page==0:
		name='Nhập ID phim %sFshare[/COLOR]-%s4share[/COLOR] hoặc %stenlua[/COLOR]'%(color['fshare'],color['4share'],color['tenlua'])
		addir(name,url,icon['icon'],mode=mode,query=query,page=1,isFolder=True)
		items = re.findall('<a href="(.+?)">(.+?)</a>',makerequest(search_file))
		trang,query,items=trangtiep(query,items)
		for href,name in items:
			temp=xshare_group(re.search('[/|\.](\w{6})\.',href),1)
			if not temp:temp='icon'
			addirs(name,href,icon[temp],query='ID?'+query)
			if (items.index((href,name))>rows) and (len(items)>int(rows*1.2)):
				name=color['trangtiep']+'Trang tiep theo...trang %d[/COLOR]'%trang
				addir(name,url,mode=mode,page=trang,query='Trang'+str(trang)+'?'+query,isFolder=True)
				break
	elif page == 1:#Nhập ID mới
		idf = get_input('Hãy nhập chuỗi ID link của Fshare-4share hoặc tenlua');record=[]
		if idf is None or idf.strip()=='':return 'no'
		idf = xshare_group(re.search('(\w{10,20})',''.join(s for s in idf.split()).upper()),1)
		if len(idf)<10:mess(u'Bạn nhập ID link chưa đúng: '+idf);return 'no'
		elif len(idf)<13:
			url=check_id_fshare(idf);query='fshare'
			if url:name=doc_TrangFshare(url,icon[query],'')
			if url and name and name!='no':record.append((url,name))
		else:
			query='4share';name,url=check_id_4share(idf)
			if name:addirs(name,url,icon[query]);record.append((url,name))
			else:
				query='tenlua';name,url=check_id_tenlua(idf)
				if name:addirs(name,url,icon[query]);record.append((url,name))
		for url,name in record:
			if url not in makerequest(search_file):
				string='<a href="%s">%s</a>\n'%(url,name);makerequest(search_file,string=string,attr='a')
		if not record:mess(u'Không tìm được link có ID: '+idf);return 'no'
	elif page == 4:#Mở thư mục chia sẻ trên Fshare
		doc_TrangFshare(query,icon_path+'fshare.png','')
	return ''

def ifile_tv_page(url):
	items=[]
	try: 
		pattern='id="(\d{,6})".{,300}<a href="(.+?)".{,300}src="(.+?)".{,300}"red">(.+?)</font>'
		item = re.compile(pattern,re.DOTALL).findall(make_request(url))
		for id_tip,href,img,name in item:
			http='http://ifile.tv';href=http+href;id_htm=href.rsplit('.')[2];img=http+img;name=name.strip()
			items.append((id_tip,id_htm,href,img,name))
	except:print 'ifile_tv_page Error: '+ url
	return items #id_tip,id_htm,href,img,name

def ifile_tv_4share(url):
	items = []
	body = make_request(url)
	pattern="href='/(.+?)'>.+?</a></u>|<div class='arrow_news'> <a.+>(.+?)</a>|<img src= '(.+?)' style='width: 100%'>"
	pattern+="|<b>(.+?)</b><br/><b>|<b>(http://4share.vn.+?)</b>.{,20}<b>(.+?)</b>"
	pattern+="|href='(http://subscene.com/subtitles/.+?)'"
	category=name=img=''
	for c,n1,i,n2,url4share,size,urlsubscene in re.findall(pattern,body):
		category+=xshare_group(re.search('phim/(.+?)\.\d{,6}',c),1)+' '
		if n1:name=n1
		if n2 and not name:name=n2
		if i:img=i
		if url4share and url4share not in items:
			category=' '.join(s for s in category.split())
			name=clean_string(name)+' - '+size;url4share=urllib.unquote(url4share)
			items.append((url4share,'http://ifile.tv'+img,name,category))
		if urlsubscene and urlsubscene not in items:
			category=' '.join(s for s in category.split())
			name=clean_string(name)+' - '+size;urlsubscene=urllib.unquote(urlsubscene)
			items.append((urlsubscene,'http://ifile.tv'+img,name,category))
	return items

def ifile_update():
	items_old, id_old = read_items_old("ifiletv.xml")
	mess(u'Đang kiểm tra dữ liệu cập nhật của ifile.tv...')
	items_new = []#id_tip,id_htm,href,img,name
	for id_tip,id_htm,href,img,name in ifile_tv_page('http://ifile.tv/') :
		if id_htm not in id_old:
			for url4share,fanart,name2,catalog in ifile_tv_4share(href):
				if name in name2:fullname = name2
				else:fullname=name
				fullname=' '.join(s for s in fullname.split())
				items_new.append((id_tip,id_htm,catalog,img,fanart,url4share,fullname))
	if items_new:update_xml(items_new,items_old,"ifiletv.xml")
	else:mess(u'Không có phim mới...')
	return 'ok'
	
def read_items_old(filename):
	items_old = doc_xml(os.path.join(datapath,filename));id_old=[]
	for i in items_old:id_old.append((i[1]))
	return items_old, id_old

def read_all_filexml(fn="vaphim.xml",string_search='',lists=[],index=[]):
	if string_search:lists = lists+doc_xml(os.path.join(datapath,fn),para='search:'+string_search)
	else:lists = lists+doc_xml(os.path.join(datapath,fn))
	if not string_search:
		for id_tip,id_htm,category,img,fanart,url,name in lists:index.append((id_htm))
	return lists,index

def phimfshare_search(url,string,mode,temp=[],p=0):
	string,trang,p=trang_search(string)
	start=(int(trang)-1)*20;s=no_accent(string)
	if trang=='1':apiary=str(random.randrange(10**3,10**5))
	else:apiary=p
	url_search='https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&'
	url_search+='rsz=filtered_cse&num=20&hl=vi&prettyPrint=false&source=gcsc&gss=.com&googlehost=www.google.com&'
	url_search+='sig=23952f7483f1bca4119a89c020d13def&cx=005609294674567689888:qyuk9aoqwmg&q=%s'%urllib.quote_plus(s)
	url_search+='&start=%d&callback=google.search.Search.apiary%s&nocache'%(start,apiary)
	body=make_request(url_search)
	results=xshare_group(re.search('(\(\{"cursor".+?\}\));',body),1)
	if not results:return 'no'
	true='true';false='false'#xu ly loi khi results co chua bien true,false
	results=eval(results)
	for i in results["results"]:
		fanart=''
		if 'richSnippet' in i and 'cseThumbnail' in i['richSnippet'] and 'src' in i['richSnippet']['cseThumbnail']:
			fanart=i['richSnippet']['cseThumbnail']['src']
		if 'url' not in i:continue
		mess(i['url'].split('/')[len(i['url'].split('/'))-2])
		response=make_request(i['url'])
		name=xshare_group(re.search('<title> (.+?)</title>',response),1)
		if not name:continue
		img=xshare_group(re.search('<img src="(.+?)" border="0" alt="" />',response),1)
		name=' '.join(s for s in re.sub('\[.+?\]|\(.+?\)|\|.*\||MuLtI|Fshare|fshare|amp;','',name).split())
		for server,link in getlinkPFS(response):
			addirs(name,link,img,fanart)
	trangtiep_google_custom(url,results,string,mode,trang,start,apiary)
	return ''

def hdvn_search(url,string,mode,temp=[],p='0'):
	string,trang,p=trang_search(string)
	start=(int(trang)-1)*20
	if trang=='1':apiary=str(random.randrange(10**3,10**5))
	else:apiary=p
	url_search='https://www.googleapis.com/customsearch/v1element?'
	url_search+='key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=20&'
	url_search+='hl=vi&prettyPrint=false&source=gcsc&gss=.com&sig=23952f7483f1bca4119a89c020d13def&'
	url_search+='cx=006389339354059003744:dxv8n47myyg&googlehost=www.google.com&start=%d&'%start
	url_search+='q=%s&callback=google.search.Search.apiary%s&nocache'%(urllib.quote_plus(string),apiary)
	body=make_request(url_search)
	results=xshare_group(re.search('(\(\{"cursor".+?\}\));',body),1)
	if not results:return 'no'
	results=eval(results)
	for i in results["results"]:
		fanart=''
		if 'richSnippet' in i and 'cseThumbnail' in i['richSnippet'] and 'src' in i['richSnippet']['cseThumbnail']:
			fanart=i['richSnippet']['cseThumbnail']['src']
		if 'url' in i:
			j=hdvn_get_link(i['url'],fanart)
			if j:temp+=j
	if 'cursor' in results and 'pages' in results['cursor']:
		if str(int(start)+20) in ' '.join(s['start'] for s in results['cursor']['pages']) and len(temp)<10 and int(trang)%3>0:
			trang=str(int(trang)+1)
			return hdvn_search(url,'%s?%s?%s'%(string,trang,p),mode,temp)
	trangtiep_google_custom(url,results,string,mode,trang,start,apiary)
	return ''

def trangtiep_google_custom(url,results,string,mode,trang,start,apiary):
	if 'cursor' in results and 'pages' in results['cursor']:
		if str(int(start)+20) in ' '.join(s['start'] for s in results['cursor']['pages']):
			trang=str(int(trang)+1)
			name=color['trangtiep']+'Trang tiep theo...trang %s[/COLOR]'%trang
			addir(name,url,icon[url.split('.')[0]],mode=mode,page=4,query='%s?%s?%s'%(string,trang,apiary),isFolder=True)

def fourshare_search(url,string,mode,temp=[],p=0):
	string,trang,p=trang_search(string)	
	href='http://4share.vn/search?page=%s&str=%s'%(trang,urllib.quote_plus(string))#+' mkv'
	pattern="<a target='_blank' href='(.+?)'>(.+?)</a><.{,40}>(.+?)</td>"
	body=make_request(href)
	items = re.findall(pattern,body);temp=[]
	for href,name,size in items:
		if os.path.splitext(name)[1][1:].lower().strip() not in media_ext:continue
		name=name+' - '+size;href='http://4share.vn%s'%href
		if href not in temp:temp.append(href);addirs(name,href)
	trang=str(int(trang)+1)
	if trang in ' '.join(s for s in re.findall("search\?page=(\d{,2})",body)) and len(temp)<10 and int(trang)%15>0:
		return fourshare_search(url,'%s?%s'%(string,trang),mode,temp,p)
	p=str(int(p)+1)
	if trang in ' '.join(s for s in re.findall("search\?page=(\d{,2})",body)):
		addir(color['trangtiep']+'Trang tiep theo...trang %s[/COLOR]'%p,url,icon['4share'],mode=mode,page=4,query='%s?%s?%s'%(string,trang,p),isFolder=True)
	return ''

def trang_search(string):
	if len(string.split('?'))==3:p=string.split('?')[2];trang=string.split('?')[1];string=string.split('?')[0]
	elif len(string.split('?'))==2:p=1;trang=string.split('?')[1];string=string.split('?')[0]
	else:p=trang='1'
	return string,trang,p

def tenlua_search(url,string,mode,temp=[]):
	string,trang,p=trang_search(string)
	href='https://api2.tenlua.vn/search?keyword=%s&page=%s'%(urllib.quote_plus("%s"%string),trang)
	response = make_request(href,json=1)
	if int(response['pagging']['total'])==0:mess(u'Không tìm được tên phim phù hợp');return 'no'
	for item in response['items']:
		if item is None or item['ext'] not in media_ext:continue
		idf=item['h']
		link=tenlua_get_detail_and_starting(idf)
		if link["type"]=="none":continue
		elif link["type"]=="file":name=link['n'];href="https://www.tenlua.vn/download/%s"%idf
		elif link["type"]=="folder":name=link["folder_name"];href="https://www.tenlua.vn/fm/folder/%s"%idf
		if href not in temp:temp.append(href);addirs(name,href,icon['tenlua'])
	trang=str(int(trang)+1)
	if int(response['pagging']['pages'])>=int(trang) and len(temp)<10 and int(trang)%15>0:
		return tenlua_search(url,'%s?%s?%s'%(string,trang,p),mode,temp)
	p=str(int(p)+1)
	if int(response['pagging']['pages'])>=int(trang):
		name=color['trangtiep']+'Trang tiep theo...trang %s[/COLOR]'%p
		addir(name,url,icon['tenlua'],mode=mode,page=4,query='%s?%s?%s'%(string,trang,p),isFolder=True)
	return ''

def ifile_search(url,string,mode,temp=[]):
	string,trang,p=trang_search(string)	
	url_search = 'http://ifile.tv/search?search_module=phim&search_name=1&'
	url_search += 'search_content=1&time_sort=new&search_string="%s"'%urllib.quote_plus(string)
	bodys = re.findall("<td>(.*?)</b>",urlfetch.get(url_search).body);items = []
	for body in bodys:
		items+=re.findall("<a.+href='(.+?)'.+src='(.+?)'.+(\d{5}).+>(.+?)</a>",body)
	if not items:mess(u'Không tìm được tên phim phù hợp');return 'no'
	items_xml,id_xml = read_all_filexml(fn="ifiletv.xml")
	for href,img,id_htm,name in items:
		if id_htm in id_xml:
			index = id_xml.index(id_htm)
			while id_xml[index] == id_htm:
				temp.append((items_xml[index]));index +=1 
		else:
			for url4share,fanart,name2,catalog in ifile_tv_4share('http://ifile.tv'+href):
				temp.append(('',id_htm,catalog,img,fanart,url4share,name))
	for id_tip,id_htm,catalog,img,fanart,href,name in temp:addirs(name,href,img,fanart)
	return ''
				
def vaphim_search(url,string,mode,temp=[],p=0):
	string,trang,p=trang_search(string)
	url_search='http://vaphim.com/page/%s/?s=%s'%(trang,urllib.quote_plus(string))
	items = vaphim_page(url_search)
	if not items:
		mess(u'Không tìm được tên phim phù hợp');return 'no'
	items_xml,id_xml = read_all_filexml()
	for id_tip,id_htm,category,href in items:
		if id_htm in id_xml:
			index = id_xml.index(id_htm)
			while id_xml[index] == id_htm:
				temp.append((items_xml[index]));index +=1 
		else:
			mess(href)
			for img,fanart,link,name in vp2fshare(href):
				temp.append((id_tip,id_htm,category,img,fanart,link,name))
	for id_tip,id_htm,catalog,img,fanart,href,name in temp:addirs(name,href,img,fanart)
	pattern="class='pages'>(.+?)<.+span><a href='(.+?)' class='page larger'>(\d{,3})</a>"
	page_tag=re.search(pattern,make_request(url_search))
	if page_tag:
		trang=str(int(trang)+1)
		name=color['trangtiep']+'Tiep theo %s...trang %s[/COLOR]'%(xshare_group(page_tag,1),xshare_group(page_tag,3))
		addir(name,url,icon[url.split('.')[0]],mode=mode,page=4,query='%s?%s?%s'%(string,trang,p),isFolder=True)
	return ''
	
def internal_search(url,string,mode,temp=[],p=0):
	string,trang,p=trang_search(string);items=[]
	if trang=='1':
		for fn in ['vaphim.xml','ifiletv.xml','phimfshare.xml','hdvietnam.xml']:
			items,index=read_all_filexml(fn=fn,string_search=".*".join(string.split()),lists=items)
		items=sorted(items,key=lambda l:no_accent(l[3]).lower());p=str(len(items))
		if not items:mess(u'Không tìm thấy phim nào có chuổi phù hợp');return
		if len(items)>(rows+rows/2):makerequest(os.path.join(data_path,'temp.txt'),string=str(items),attr='w')
	else:f=open(os.path.join(data_path,'temp.txt'));items=eval(f.readlines()[0]);f.close()

	trang=int(trang);del items[:rows*(trang-1)]
	if len(items)>(rows+rows/2):
		del items[rows:];trang=str(trang+1)
	else:trang=''
	for img,fanart,href,name in items:addirs(name,href,img,fanart)
	if trang:
		name=color['trangtiep']+'Trang tiep theo...trang %s/%s[/COLOR]'%(trang,str(int(p)/rows+1))
		addir(name,url,icon['xshare'],mode=mode,page=4,query='%s?%s?%s'%(string,trang,p),isFolder=True)

def get_file_search(url,mode):
	srv=url.split('.')[0]
	if mode==2:site='Google '
	else:site=''
	name=color['search']+'%sSearch[/COLOR] trên %s%s: [/COLOR]Nhập chuỗi tìm kiếm mới'%(site,color[srv],url)
	addir(name,url,icon[srv],mode=mode,page=1,query='INP',isFolder=True)
	if myaddon.getSetting('history')=='true':
		items = re.findall('<a>(.+?)</a>',makerequest(search_file))
		for string in items:
			addir(string,url,icon[srv],query='Search?'+string,page=4,mode=mode,isFolder=True)

def get_string_search(url):
	query = get_input('Nhập chuổi tên phim cần tìm trên %s'%url)
	if query:
		query = ' '.join(s for s in query.replace('"',"'").replace('?','').split() if s!='')
		makerequest(search_file,string='<a>%s</a>\n'%query,attr='a')
	return query

def xshare_search(url,query,mode,page,items=[]):#13
	if page==0:get_file_search(url,mode)
	elif page==1:
		query=get_string_search(url)
		if query:return xshare_search(url,query,mode,4,items)
		else:return 'no'
	elif page==4:
		query=no_accent(query)
		if url=='vaphim.com':vaphim_search(url,query,mode)
		elif url=='phimfshare.com':phimfshare_search(url,query,mode)
		elif url=='tenlua.vn':tenlua_search(url,query,mode)
		elif url=='4share.vn':fourshare_search(url,query,mode)
		elif url=='ifile.tv':ifile_search(url,query,mode)
		elif url=='hdvietnam.com':hdvn_search(url,query,mode)
		elif url=='xshare.vn':internal_search(url,query,mode)
	return ''
	
def updatePFS():#6+
	items=rss_content('http://phimfshare.com/external.php?type=RSS2')
	content_new=''
	fphimfshare=os.path.join(datapath,'phimfshare.xml')
	content_old=makerequest(fphimfshare)
	idf_old=re.findall('<a id="(.+?)" server',content_old)
	for item in items:
		idf=xshare_group(re.search('-(\d{5})',item.findtext('link')),1)
		if not idf or idf in idf_old:continue
		name=re.sub('\[.*\]|\(.*\)|\|.*\|','',item.findtext('title')).strip()
		content=item.findtext('contentencoded')
		img=xshare_group(re.search('img src="(.+?jpg)["|?| ]',content),1)
		for server,link in getlinkPFS(content):
			if link not in content_new:
				content_new+='<a id="%s" server="%s" href="%s" img="%s">%s</a>\n'%(idf,server,link,img,name)
	if content_new:
		makerequest(fphimfshare,string=content_new.encode('utf-8'),attr='a')
		mess('PhimFshare.com data Auto update completed')

def getlinkPFS(content):#6+
	items=[]
	pattern='(https?://www.fshare.vn/\w{4,6}/\w{10,14})|(http://4share.vn/./\w{14,20})|(https?://w?w?w?/?tenlua.vn/.*?)[ |"|<]'
	for links in re.findall(pattern,content):
		if links:
			for link in links:
				idf=xshare_group(re.search('(\w{10,20})',link),1)
				if idf:
					link=link.lower()
					if 'fshare.vn/file' in link:url='https://www.fshare.vn/file/%s'%idf.upper();server="fshare"
					elif 'fshare.vn/folder' in link:url='https://www.fshare.vn/folder/%s'%idf.upper();server="fshare"
					elif 'tenlua.vn' in link and ('folder/' in link or '#download' in link) and len(idf)>16:
						url='https://tenlua.vn/fm/folder/%s'%idf;server="tenlua"
					elif 'tenlua.vn' in link and len(idf)>16:url='https://tenlua.vn/download/%s'%idf;server="tenlua"
					elif '4share.vn' in link:url=link;server="4share"
					else:continue
					items.append((server,url))
	return items
	
def phimFshare(name,url,mode,page,query):#6
	fphimfshare=os.path.join(datapath,'phimfshare.xml')
	home='http://phimfshare.com/'
	if query=='phimfshare.com':get_file_search(url,mode);return ''
	elif page==4 and name==query:return phimFshare('Search',url,mode,page,query)
	elif name=='Search':
		search_string = urllib.quote_plus(query)
		url='https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&'
		url+='rsz=filtered_cse&num=15&hl=vi&prettyPrint=false&source=gcsc&gss=.com&'
		url+='sig=23952f7483f1bca4119a89c020d13def&cx=005609294674567689888:qyuk9aoqwmg&q='+search_string
		url+='&googlehost=www.google.com&callback=google.search.Search.apiary'
		body=urlfetch.get(url).body
		items =re.findall('()"url":"(http://phimfshare.com/.+?)"()()',body)
		if not items:mess(u'Không tìm thấy phim có chứa chuổi tìm kiếm');return 'no'
	elif query=="INP":
		query=get_string_search(url)
		if query:return phimFshare('Search',url,mode,page,query)
		else:return 'no'
	elif query=='PhimMoi':
		body=urlfetch.get(home).body
		items=re.findall('()<a href="(.+?)" ()class="title">(.+?)</a>',body)
	else:
		if home not in url:url=home+url+'/'
		body=urlfetch.get(url).body
		pattern='<img class="preview" src="(.+?)" .+? class=".+?" href="(.+?)" id="thread_title_(.+?)">(.+?)</a>'
		items=re.findall(pattern,body)
	
	content_old=makerequest(fphimfshare);content_new=''
	for img,href,idf,name in items:
		if not idf or len(idf)<5:
			idf=xshare_group(re.search('-(\d{5})',href),1)
			if not idf:continue
		items_old=re.findall('<a id="%s" server="(.+?)" href="(.+?)" img="(.*?)">(.+?)</a>'%idf,content_old)
		if items_old:
			for ser_,href_,img_,name_ in items_old:
				addirs(name_,href_,img_,img_)
		else:
			mess(href.split('/')[len(href.split('/'))-2])
			response=urlfetch.get(href).body
			temp=xshare_group(re.search('<title> (.+?)</title>',response),1)
			if temp:name=temp
			elif not name:continue
			if not img:img=xshare_group(re.search('<img src="(.+?)" border="0" alt="" />',response),1)
			name=' '.join(s for s in re.sub('\[.+?\]|\(.+?\)|MuLtI|Fshare|fshare','',name).split())
			for server,link in getlinkPFS(response):
				if link not in content_new:
					content_new+='<a id="%s" server="%s" href="%s" img="%s">%s</a>\n'%(idf,server,link,img,name)
				addirs(name,link,img,img)
	if content_new:makerequest(fphimfshare,string=content_new,attr='a')
	href=xshare_group(re.search('<a rel="next" href="(.+?)" title=".+?">',body),1)
	if href:
		if not page:page=1
		page+=1;name=color['trangtiep']+'Trang tiếp theo - Trang '+str(page)+' ...[/COLOR]'
		addir(name,href,icon_path+'fshare.png',mode=mode,page=page,query=query,isFolder=True)
	return ''

def rss_content(url):
	from xml.etree import ElementTree as etree
	reddit_file = make_request(url)
	reddit_file = reddit_file.replace('content:encoded','contentencoded')
	try:
		reddit_root = etree.fromstring(reddit_file)
		items=reddit_root.findall('channel/item')
	except:
		mess('Update rss %s fail'%url)
		items=[]
	return items
	
def correct_link(url):
	if 'tenlua.vn' in url:idf=xshare_group(re.search('(\w{16,20})',url),1)
	elif 'subscene.com' in url and '...' not in url:idf='ok'
	else:idf=xshare_group(re.search('(\w{10,20})',url),1)
	if idf:
		url=url.lower()
		if 'fshare.vn/file' in url:url='https://www.fshare.vn/file/%s'%idf.upper()
		elif 'fshare.vn/folder' in url:url='https://www.fshare.vn/folder/%s'%idf.upper()
		elif 'tenlua.vn' in url and ('folder/' in url or '#download' in url) and len(idf)>16:
			url='https://tenlua.vn/fm/folder/%s'%idf
		elif 'tenlua.vn' in url and len(idf)>16:url='https://tenlua.vn/download/%s'%idf
		elif '4share.vn' or 'subscene.com'in url:url=url
	else:url=''
	return url

def hdvn_update():
	file_hdvn=os.path.join(datapath,"hdvietnam.xml")
	hdvn_content=makerequest(file_hdvn)
	items = rss_content('http://www.hdvietnam.com/diendan/external.php?type=RSS2')
	pattern_link='(https?://www.fshare.vn/\w{4,6}/\w{10,14})|(http://4share.vn/./\w{14,20})|(https?://w?w?w?/?tenlua.vn/.*?)[ |"|<]|(http://subscene.com/subtitles/.+?)[ |"|\'|<]'
	dir_items=[];string=''
	index_old=re.findall('href="(.+?)"',hdvn_content)
	temp=list();homnay=datetime.date.today().strftime("%d/%m/%Y")
	for item in items:
		contentencoded=item.findtext('contentencoded')
		img=xshare_group(re.search('a href="([\w|:|/|\.]+\.jpg)" class="highslide"',contentencoded),1)
		links=re.findall(pattern_link,contentencoded)
		if not links:continue
		name=re.sub('\{.*\}|\[.*\]|\(.*\)|\|.*\|','',item.findtext('title')).strip()
		for link in links:
			for url in link:
				url=correct_link(url)
				if not url or url in temp:continue
				temp.append(url);dir_items.append((url,img,name))
				if url not in index_old:
					string+='<a date="%s" href="%s" img="%s">%s</a>\n'%(homnay,url,img,name)
	if string:makerequest(file_hdvn,string=string.encode('utf-8'),attr='a')

def hdvietnam(query,mode):
	if query=='HDV':query=homnay;hdvn_update()
	file_hdvn=os.path.join(datapath,"hdvietnam.xml")
	hdvn_content=makerequest(file_hdvn)
	items=re.findall('date="%s" href="(.+?)" img="(.+?)">(.+?)</a>'%query,hdvn_content)
	for href,img,name in sorted(items,key=lambda l:no_accent(l[2])):addirs(name,href,img,img)
	ngaytruoc=hdvn_ngaytruoc(query,hdvn_content)
	if ngaytruoc!=query:
		name=color['trangtiep']+"Thông tin ngày %s[/COLOR]"%ngaytruoc
		addir(name,"HDV",icon["icon"],mode=mode,query=ngaytruoc,isFolder=True)

def hdvn_ngaytruoc(query,content):
	items=re.findall('date="(.+?)"',content);ngaytruoc=''
	if len(items)>0:
		ngaytruoc=items[0]
		for i in items:
			if i==query:break
			ngaytruoc=i
	return ngaytruoc

def data_update():
	ngay=datetime.date.today().strftime("%Y%m%d00");gio=datetime.datetime.now().strftime("%H")
	last_update=myaddon.getSetting('last_update')
	try:
		if ngay>last_update:vp_update();ifile_update();myaddon.setSetting('last_update',ngay)
		if int(gio)-int(last_update[8:])>4:
			hdvn_update();updatePFS();vp_update_rss()
			myaddon.setSetting('last_update',last_update[:8]+gio)
			mess(u'Đã cập nhật danh mục phim từ các dữ liệu RSS')
	except:mess('Data update error');pass

def mkdir_temp(tempdir,delete=True):
	tempdir=temp=xbmc.translatePath(os.path.join(thumuccucbo,'temp'))
	if os.path.exists(tempdir) and delete:
		import shutil
		try:shutil.rmtree(tempdir)
		except:
			xbmc.sleep(1000)
			try:shutil.rmtree(tempdir)
			except:pass
	if not os.path.exists(tempdir):
		try:os.mkdir(tempdir)
		except:
			xbmc.sleep(1000)
			try:os.mkdir(tempdir)
			except:mess(u'Không tạo được thư mục temp');temp=''
	return temp

def subscene(name,url,query):#,img='',fanart='',query=''
	if query=='subscene.com':
		href = get_input('Hãy nhập link của sub trên subscene.com','http://subscene.com/subtitles/')
		if href is None or href=='' or href=='http://subscene.com/subtitles/':return 'no'
	else:href=url
	if not re.search('\d{5,10}',href):
		if not os.path.basename(href):href=os.path.dirname(href)
		pattern='<a href="(/subtitles/.+?)">\s+<span class=".+?">\s*(.+?)\s+</span>\s+<span>\s+(.+?)\s+</span>'
		subs=re.findall(pattern,urlfetch.get(url=href,headers={'Cookie':'LanguageFilter=13,45'}).body)
		for url,lang,name in subs:
			if '/english/' in url:name='Eng '+name
			else:name='[COLOR red]Vie[/COLOR]-'+name
			addirs(name,'http://subscene.com'+url,query='download')
		return ''
	pattern='<a href="(.+?)" rel="nofollow" onclick="DownloadSubtitle.+">'
	downloadlink='http://subscene.com' + xshare_group(re.search(pattern,make_request(href)),1)
	if len(downloadlink)<20:mess(u'Không tìm được maxspeed link sub');return
		
	typeid="srt"
	body=make_request(downloadlink)
	tempfile = os.path.join(thumuccucbo, "subtitle.sub")
	f = open(tempfile, "wb");f.write(body);f.close()
	f = open(tempfile, "rb");f.seek(0);fread=f.read(1);f.close()
	if fread == 'R':	typeid = "rar"
	elif fread == 'P':typeid = "zip"

	tempfile = os.path.join(thumuccucbo, "subtitle." + typeid)
	if os.path.exists(tempfile):
		try:os.remove(tempfile)
		except:return
	os.rename(os.path.join(thumuccucbo, "subtitle.sub"), tempfile)
	if os.path.exists(tempfile):mess(u'Đã tải sub vào Thư mục riêng trên máy: %s'%str2u(name))
	if typeid in "rar-zip":
		tempath=thumuccucbo
		if 'Eng' in name and myaddon.getSetting('trans_sub')=='true':
			tempath=mkdir_temp('temp')
			if not tempath:return 'no'
		xbmc.sleep(500)
		try:xbmc.executebuiltin(('XBMC.Extract("%s","%s")'%(tempfile,tempath)).encode('utf-8'), True)
		except:pass
		if tempath!=thumuccucbo:
			exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass"];sub_list=[]
			for root, dirs, files in os.walk(tempath):
				for f in files:
					f=re.sub(',|"|\'','',f)
					file = os.path.join(root, f)
					filesub=os.path.join(thumuccucbo, f)
					if os.path.splitext(file)[1] in exts:
						sub_list.append(file)
						mess(u'Google đang dịch sub từ tiếng Anh sang tiếng Việt', timeShown=20000)
						try:
							tempfile=xshare_trans(file,tempath)
							os.remove(file)
							if os.path.exists(filesub):os.remove(filesub)
							os.rename(tempfile,filesub)
							mess(u'Đã dịch xong sub từ tiếng Anh sang tiếng Việt') 
						except:mess(u'Không dịch được sub từ tiếng Anh sang tiếng Việt') 

	return 'ok'

def xshare_trans(sourcefile,tempath):
	tempfile = os.path.join(tempath, "temp"+os.path.splitext(sourcefile)[1])
	fs=open(sourcefile);ft=open(tempfile,'w');lineslist=[];substring=''
	for line in fs:
		if re.search('[a-zA-Z]',line):
			substring+='+'.join(''.join(re.split('<.+?>',line.replace('"',''))).strip().split())+'+xshare+'
			lineslist.append('xshare')
		else:
			lineslist.append(line.strip()+'\n')
			if len(substring)>1500:
				write_trans(ft,substring,lineslist)
				substring='';lineslist=[]
	if len(substring)>0:write_trans(ft,substring,lineslist)
	fs.close();ft.close()
	return tempfile

def write_trans(fo,string,m):
	translist=google_trans(string);j=0
	for i in m:
		if i=='xshare':
			try:fo.write(translist[j].strip()+'\n');j+=1
			except:pass
		else:fo.write(i)
    
def google_trans(s):
	hd={'User-Agent':'Mozilla/5.0','Accept-Language':'en-US,en;q=0.8,vi;q=0.6','Cookie':''}
	url='https://translate.google.com.vn/translate_a/single?oe=UTF-8&tl=vi&client=t&hl=vi&sl=en&dt=t&ie=UTF-8&q=%s'%s
	body= urlfetch.fetch(url=url,headers=hd).body
	body=body.replace(',,"en"','').replace('[[[','').replace(']]]','')
	result=''
	for i in body.split('],['):
		research=xshare_group(re.search('"(.+?)","(.+?)"',i),1)
		if research:result+=research+' '
		else:print '%s :not research'%i
	return result.replace('Xshare','xshare').split('xshare')

def fptplay(name,url,img,mode,page,query):
	if query=="FPP":
		body=make_request('http://fptplay.net')
		name=color['search']+"Search trên fptplay.net[/COLOR]"
		addir(name,"fptplay.net/tim-kiem",icon['fptplay'],mode=mode,query="FPS",isFolder=True)
		name=color['fptplay']+'Trang chủ fptplay.net[/COLOR]'
		addir(name,"http://fptplay.net",icon['fptplay'],mode=mode,query='FP0',isFolder=True)
		start='top_menu reponsive';end='top_listitem';body=body[body.find(start):body.find(end)]
		for href,title in re.findall('<li ><a href="(http://fptplay.net/danh-muc/.+?)">(.+?)</a></li>',body):
			title=color['fptplay']+fptplay_2s(title)+'[/COLOR]'
			addir(title,href,icon['fptplay'],mode=mode,query='FP2',isFolder=True)
	elif query=="FPS":get_file_search(url,mode)
	elif query=="INP":
		query=get_string_search(url)
		if query:return fptplay(name,url,img,mode,page,query)
		else:return 'no'
	elif url=="fptplay.net/tim-kiem":
		search_string = urllib.quote(query)
		url='http://fptplay.net/show/more?type=search&stucture_id=key&page=1&keyword=%s'%search_string
		return fptplay(name,url,img,mode,page,query='FP3')
	elif query=="FP0":
		body=make_request('http://fptplay.net')
		name=color['fptplay']+'Phổ biến hiện nay[/COLOR]'
		addir(name,'phim_popular',icon['fptplay'],mode=mode,query='FP1',isFolder=True)
		name=color['fptplay']+'Đặc sắc[/COLOR]'
		addir(name,'phim_trending',icon['fptplay'],mode=mode,query='FP1',isFolder=True)
		pattern='<a href="(.+?)" title="(.+?)" class="pull-left btn_arrow_right"></a>'
		items=re.findall(pattern,body)
		for href,title in items:
			title=color['fptplay']+fptplay_2s(title)+'[/COLOR]'
			addir(title,href,icon['fptplay'],mode=mode,query='FP1',isFolder=True)
	elif query=="FP1":
		body=make_request('http://fptplay.net')
		if 'phim_popular' in url:start='data-tooltip="phim_popular';end='data-tooltip="phim_trending'
		elif 'phim_trending' in url:start='data-tooltip="phim_trending';end='id="selTab_5284685d169a585a2449c489"'
		elif 'phim' in url:start='id="selTab_5284685d169a585a2449c489"';end='id="selTab_52847232169a585a2449c48c'
		elif 'tv-show' in url:start='id="selTab_52847232169a585a2449c48c';end='id="selTab_54fd271917dc136162a0c'
		elif 'thieu-nhi' in url:	start='id="selTab_54fd271917dc136162a0cf2d';end='id="selTab_52842df7169a580a79169'
		elif 'the-thao' in url:start='id="selTab_52842df7169a580a79169efd"';	end='id="selTab_5283310e169a585a05b920d'
		elif 'ca-nhac' in url:start='id="selTab_5283310e169a585a05b920de"';end='id="selTab_52842dd3169a580a79169efc'
		elif 'tong-hop' in url:start='id="selTab_52842dd3169a580a79169efc"';end='</body>'
		body=body[body.find(start):body.find(end)]
		pattern='<a href=".+?-(\w+)\.html".*alt="(.+?)"'
		items=re.findall(pattern,body);temp=[]
		for id,title in items:
			if id not in temp:temp.append(id);fptplay_getlink(id,fptplay_2s(title),mode)
	elif query=="FP2":
		pattern='<a href="(http://fptplay.net/the-loai/.+?)" title="(.+?)"'
		items=re.findall(pattern,make_request(url))
		for href,name in items:
			name=color['fptplay']+fptplay_2s(name)+"[/COLOR]";id=xshare_group(re.search('(\w{22,26})',href),1)
			data='type=new&keyword=undefined&page=1&stucture_id=%s'%id;url='http://fptplay.net/show/more?%s'%data
			addir(name,url,icon["fptplay"],mode=mode,query="FP3",isFolder=True)
	elif query=="FP3":
		try:body=urlfetch.post(url).body
		except:mess(u'Lỗi get data từ fptplay.net');return 'no'
		items=re.findall('<a href=".+-(\w+)\.html".+class="title">(.+?)</a>',body)
		for id,title in items:fptplay_getlink(id,fptplay_2s(title),mode)
		if len(items)>35:
			page=xshare_group(re.search('page=(\d{1,3})',url),1);page=str(int(page)+1);
			url=re.sub('page=\d{1,3}','page='+page,url)
			name=color['trangtiep']+"Trang tiếp theo - Trang %s[/COLOR]"%page
			addir(name,url,icon["fptplay"],mode=mode,query="FP3",isFolder=True)
		elif not items:mess(u'Không tìm thấy dữ liệu');return 'no'
	elif query=="FP4":fptplay_getlink(url,name,mode,dir=False)
	elif query=='play':xbmcsetResolvedUrl(url)
	return ''
	
def fptplay_2s(string):
	return ' '.join(re.sub('&.+;',xshare_group(re.search('&(\w).+;',s),1),s) for s in string.split())

def fptplay_getlink(id,name,mode,dir=True):
	try:
		json=urlfetch.post('http://fptplay.net/show/getlink?id=%s&episode=1&mobile=web'%id).json
		if dir:
			url = json['quality'][0]['url'][0]['url']
			img = json['quality'][0]['thumb']
			title = json['quality'][0]['title']
			if len(json['quality'])==1:addir(name.strip(),url,img,img,mode=mode,query='play')
			else:addir(color['fptplay']+name.strip()+"[/COLOR]",id,img,img,mode=mode,query='FP4',isFolder=True)
		else:
			for i in json['quality']:
				url = i['url'][0]['url']
				img = i['thumb']
				title = re.sub('\[.{,20}\]','',name.strip())+' - '+i['title'].encode('utf-8')
				addir(title,url,img,img,mode=mode,query='play')
	except:pass

def megabox(name,url,mode,page,query):
	home='http://phim.megabox.vn/'
	if query=='megabox.vn':get_file_search(url,mode)
	elif query=="INP":
		query=get_string_search(url)
		if query:return megabox(query,url,mode,page,query)
		else:return 'no'
	elif query==name:
		search_string = urllib.quote_plus(query)
		try:#body=make_request('http://phim.megabox.vn/search/index?keyword=%s'%search_string);items=[]
			body=urlfetch.post('http://phim.megabox.vn/tim-kiem?keyword=%s'%search_string).body;items=[]
		except:return 'no'
		pattern='a class=".+?" href="(.+?)".*<h3 class=.H3title.>(.+?)</h3>.*\s.*src="(.+?)"|<div class="gb-view-all">.?<a href="(.+?)">(.+?)</a>'
		links=re.findall(pattern,body)
		if not links:mess(u'Không tìm thấy dữ liệu phù hợp');return 'no'
		for href,name,img,link,title in links:
			if not link:items.append((href,name,img))
			else:
				megabox_load_menu(items,mode);items=[]
				if 'phim-le' in link:title=color['search']+title+' - phim lẻ[/COLOR]'
				else:title=color['search']+title+' - phim bộ[/COLOR]'
				addir(title,link,icon['megabox'],mode=mode,query="MG4",isFolder=True)
		if items:megabox_load_menu(items,mode)
	elif query in 'MGL-MGS':
		if query=='MGL':href='http://phim.megabox.vn/phim-le'
		else:href='http://phim.megabox.vn/phim-bo'
		body=make_request(href)
		if url in 'MGL-MGS':
			body=body[body.find('<ul id="gen">'):body.find('<ul id="country">')]
			name=color['megabox']+'Tất cả thể loại[/COLOR]'
			addir(name,'MGQ',icon['megabox'],mode=mode,page=0,query="MGL",isFolder=True)
			for value,name in re.findall("<li value='(\d{1,2})' >(.+?)</li>",body):
				name=color['megabox']+name+'[/COLOR]'
				addir(name,'MGQ',icon['megabox'],mode=mode,page=int(value),query=query,isFolder=True)
		elif url=='MGQ':
			body=body[body.find('<ul id="country">'):body.find('<ul id="other">')]
			name=color['megabox']+'Tất cả Quốc gia[/COLOR]'
			url=href+'?cat=1&gen=%d'%page
			addir(name,url,icon['megabox'],mode=mode,query="MG4",isFolder=True)
			for value,name in re.findall("<li value='(\d{1,2})' >(.+?)</li>",body):
				name=color['megabox']+name+'[/COLOR]'
				url=href+'?cat=1&gen=%d&country=%s'%(page,value)
				addir(name,url,icon['megabox'],mode=mode,page=int(value),query="MG4",isFolder=True)
	elif query=='MGB':
		body=make_request(home,headers=hd);open_category("MGB")
		for href,name in re.findall('<li><a href="(.+?)" title="">(.+?)</a></li>',body):
			if 'Clip' in name:continue
			addir(color['megabox']+name+'[/COLOR]',href,icon['megabox'],mode=mode,query='MG4',isFolder=True)
	elif query=='MG0':
		body=make_request(home)
		for name in re.findall('"H2title">(.+?)</h2>',body):
			if 'Phim sắp chiếu' in name or 'clip' in name:continue
			if 'Phim Lẻ Mới Nhất' in name:
				content=make_request('http://phim.megabox.vn/ajaxschedule/home/?data=1',json=1)
				href=re.search('"H2title"><a href="(.+?)" title="">(.+?)</h2>',content['event'].encode('utf-8'))
				if href:
					title=color['megabox']+xshare_group(href,2)+'[/COLOR]'
					addir(title,xshare_group(href,1),icon['megabox'],mode=mode,query='MG1',isFolder=True)
			href=re.search('href="(.+?)">(.+?)</a>',name)
			if not href:
				name=color['megabox']+re.sub('<.{,4}>','',name)+'[/COLOR]'
				addir(name,home,icon['megabox'],home,mode=mode,query='MG1',isFolder=True)
			else:
				name=color['megabox']+xshare_group(href,2)+'[/COLOR]'
				addir(name,xshare_group(href,1),icon['megabox'],mode=mode,query='MG1',isFolder=True)
	elif query=='MG1':
		if home not in url:url=home+url
		body=make_request(url)
		if 'megabox' in name.lower():
			#pattern="<li><a href='(.+?)'.?><img src='(.+?)' alt='Banner - (.+?)''.?></a>"
			pattern="<li><a href='(.+?)'.?><img src='(.+?)'.+?<a href='.+?'>(.+?)</a>"
			items1=re.findall(pattern,body);items=[]
			for href,img,name in items1:items.append((href,name,img))
			megabox_load_menu(items,mode)
		elif 'top 10 phim' in name.lower():
			pattern='<a class="tooltip thumb" href="(.+?)".+<h3 class=.H3title.>(.+?)</h3>.*\s.*<img src="(.+?)"'
			megabox_load_menu(re.findall(pattern,body),mode)
		elif 'xem' in name.lower():#xem nhieu nhat
			pattern='<a class=.thumb. title="" href="(.+?)">.*\s.*<img alt=.Poster (.+?). src="(.+?)"/>'
			items=re.findall(pattern,body)
			if 'phim le' in no_accent(name).lower():del items[20:]
			elif 'phim bo' in no_accent(name).lower():del items[:20];del items[20:]
			elif 'show' in no_accent(name).lower():
				temp=[]
				for i in items:
					if 'megabox.vn/show' in i[0]:temp.append((i))
				items=temp
			megabox_load_menu(items,mode)
		elif url!=home:
			pattern='a class=".+?" href="(.+?)".*<h3 class=.H3title.>(.+?)</h3>.*\s.*src="(.+?)"'
			megabox_load_menu(re.findall(pattern,body),mode)
	elif query=='MG2':
		body=make_request(url)
		if '/tag/' in url:
			pattern='href="(.+?)".+<h3 class=.H3title.>(.+?)</h3>.*\s.*src="(.+?)"'
			megabox_load_menu(re.findall(pattern,body),mode)
		else:
			img=xshare_group(re.search('<img alt=.+? src="(.+?)"/>',body),1)
			links=re.findall('<a onclick=.getListEps\((.+?)\).{,20} href=.{,25}>(.+?)</a>',body)
			for link in links:
				href='http://phim.megabox.vn/content/ajax_episode?id=%s&start=%s'%(link[0].split(',')[0].strip(),link[0].split(',')[1].strip())
				title='%s Tập: %s'%(name,link[1].encode('utf-8'))
				addir(title,href,img,img,mode=mode,query=os.path.dirname(url),isFolder=True)
	elif query=='MG3':
		tap=xshare_group(re.search('(\d{1,3}-\d{1,3})',name),1)
		if tap:
			for i in range(int(tap.split('-')[0]),int(tap.split('-')[1])+1):
				addir(re.sub('Banner - ','',name),link+'|'+urllib.urlencode(hd),img,img,mode=mode,query='MGP')
		body=make_request(url)
		img=xshare_group(re.search('<img alt=.+? src="(.+?)"/>',body),1)
		links=re.findall('<a onclick=.+?>(.+?)</a>',body)
		for link in links:
			addir(name+': Tập %s'%link,url,img,img,mode=mode,query='MG3',isFolder=True)
	elif query=='MG4':
		if home not in url:url=home+url
		body=make_request(url)
		pattern='a class=".+?" href="(.+?)".*<h3 class=.H3title.>(.+?)</h3>.*\s.*src="(.+?)"'
		items=re.findall(pattern,body)
		if not items:mess(u'Không tìm thấy dữ liệu phù hợp');return 'no'
		megabox_load_menu(items,mode)
		page_control=re.findall('>(\d{,3})</a></li><li class="next"><a href="(.+?(\d{1,3}).*?)">|<li class="last"><a href=".+?(\d{1,3}).*?">',body)
		if len(page_control)==2:
			name=color['trangtiep']+u'Trang tiếp theo: trang %s/%s[/COLOR]'%(page_control[0][2],page_control[0][0])
			addir(name,page_control[0][1],mode=mode,query='MG4',isFolder=True)
		elif len(page_control)==4:
			name=color['trangtiep']+u'Trang tiếp theo: trang %s/%s[/COLOR]'%(page_control[0][2],page_control[1][3])
			addir(name,page_control[0][1],mode=mode,query='MG4',isFolder=True)
	elif query=='MGP':xbmcsetResolvedUrl(url)
	elif query=='MBP':
		response=urlfetch.get(url)
		if response.status==200:
			link=xshare_group(re.search("changeStreamUrl\('(.+?)'\)",response.body),1)
		elif response.status==301:
			link=xshare_group(re.search("changeStreamUrl\('(.+?)'\)",make_request(response.headers['location'])),1)
		else:mess(u'Không get được megabox maxspeed link');return 'no' 
		xbmcsetResolvedUrl(link+'|'+urllib.urlencode(hd))
	elif len(query)>3:
		for item in make_request(url,json=1):
			name=item['name']
			img='http://img.phim.megabox.vn/728x409'+item['image_banner']
			href=query+'/%s-%s.html'%(item['cat_id'],item['content_id'])
			addir(name,href,img,img,mode=mode,query='MBP')
	return ''
	
def megabox_load_menu(items,mode):
	for href,name,img in items:
		if 'megabox.vn/clip-' in href:continue
		if os.path.splitext(href)[1][1:].lower()=='m3u8':
			addir(name.strip(),href+'|'+urllib.urlencode(hd),img,img,mode=mode,query='MGP')
			continue
		try:
			response=urlfetch.get(href)
			if response.status==301:body=make_request(response.headers['location'])
			elif response.status==200:body=response.body
			else:print response.status,href;continue
		except:continue
		links=re.findall('<a onclick=.getListEps\((.+?)\).{,20} href=.{,25}>(.+?)</a>',body)
		if len(links)==1:
			for link in links:
				folder='http://phim.megabox.vn/content/ajax_episode?id=%s&start=%s'%(link[0].split(',')[0].strip(),link[0].split(',')[1].strip())
				name='%s%s[/COLOR]: Tập %s'%(color['megabox'],name.strip(),link[1])
				addir(name,folder,img,img,mode=mode,query=os.path.dirname(href),isFolder=True)
		else:
			link=xshare_group(re.search("changeStreamUrl\('(.+?)'\)",body),1)
			if link:addir(name.strip(),link+'|'+urllib.urlencode(hd),img,img,mode=mode,query='MGP')
			else:addir(color['megabox']+name.strip()+'[/COLOR]',href,img,img,mode=mode,query='MG2',isFolder=True)

def dangcaphd(name,url,img,mode,page,query):
	home='http://dangcaphd.com/'
	if query=='DHD':
		body=make_request(home)
		name=color['search']+"Search trên dangcaphd.com[/COLOR]"
		addir(name,"dangcaphd.com/movie/search.html",icon['dangcaphd'],mode=mode,query="DHS",isFolder=True)
		name=color['dangcaphd']+'Trang chủ dangcaphd.com[/COLOR]'
		addir(name,home,icon['dangcaphd'],mode=mode,query='DC0',isFolder=True)
		for name in re.findall('</i>(.+?)<span class="caret">',body):
			addir(color['dangcaphd']+name.strip()+'[/COLOR]',home,icon['dangcaphd'],mode=mode,query='DC1',isFolder=True)
		for href,name in re.findall('<a href="(.+?)"><i class=".+?"></i>(.+?)</a>',body):
			if 'channel.html' not in href and 'product.html' not in href:
				addir(color['dangcaphd']+name.strip()+'[/COLOR]',href,icon['dangcaphd'],mode=mode,query='DC2',isFolder=True)
	elif query=="DHS":get_file_search(url,mode)
	elif query=="INP":
		query=get_string_search(url)
		if query:return dangcaphd(name,url,img,mode,page,query)
		else:return 'no'
	elif url=="dangcaphd.com/movie/search.html":
		search_string = urllib.quote_plus(query)
		url='http://dangcaphd.com/movie/search.html?key=%s&search_movie=1'%search_string
		return dangcaphd(name,url,img,mode,page,query='DC2')
	elif query=='DC0':
		body=make_request(home)
		for href,name in re.findall('<a class="title" href="(.+?)"><i class="fa fa-film "></i>(.+?)</a>',body):
			addir(color['dangcaphd']+name.strip()+'[/COLOR]',href,icon['dangcaphd'],mode=mode,query='DC2',isFolder=True)
	elif query=='DC1':
		body=make_request(home)
		if 'the loai' in  no_accent(name).lower():
			for href,name in re.findall('<a href="(http://dangcaphd.com/cat.+?)" title="(.+?)">',body):
				addir(color['dangcaphd']+name.strip()+'[/COLOR]',href,icon['dangcaphd'],mode=mode,query='DC2',isFolder=True)
		if 'quoc gia' in  no_accent(name).lower():
			for href,name in re.findall('<a href="(http://dangcaphd.com/country.+?)" title="(.+?)">',body):
				addir(color['dangcaphd']+name.strip()+'[/COLOR]',href,icon['dangcaphd'],mode=mode,query='DC2',isFolder=True)
	elif query=='DC2':
		body=re.sub('\t|\n|\r|\f|\v','',make_request(url))
		items=re.findall('<a class="product.+?" href="(.+?)" title="(.+?)">.+?<img src="(.+?)" (.+?)</li>',body)
		for href,name,img,other in items:
			if re.search('<div class="sale">.+?</div>',other):
				name=name.strip()+'[/COLOR]'+' - ('+xshare_group(re.search('<div class="sale">(.+?)</div>',other),1)+')'
				addir(color['dangcaphd']+name,href,img,mode=mode,query='DC3',isFolder=True)
			else:addir(name.strip(),href,img,mode=mode,query='DCP')
		dangcaphd_get_page_control(body,mode,query)
	elif query=='DC3':
		for _epi,_link,_sub in dangcaphd_get_link(url):
			title=re.sub('\[.+?\]','',name.split('[/COLOR]')[0])+' - Tập '+_epi.strip()
			link=_link.replace(' ','%20').strip()+'xshare'+_sub.strip()
			addir(title,link,img,mode=mode,query='DCP')
	elif query=='DCP':
		subtitle=''
		if os.path.splitext(url)[1].lower()=='.html':
			links=dangcaphd_get_link(url)
			url=links[0][1].replace(' ','%20').strip()
			if links[0][2]:subtitle=dangcaphd_download_sub(links[0][2].strip())
		else:
			if url.split('xshare')[1]:subtitle=dangcaphd_download_sub(url.split('xshare')[1])
			url=url.split('xshare')[0]
		xbmcsetResolvedUrl(url)
		if subtitle:
			xbmc.sleep(500);xbmc.Player().setSubtitles(subtitle);mess(u'Phụ đề của dangcaphd.com')
		if 'xshare' in myaddon.getSetting('mail_dchd'):
			mess(u'Bạn đang dùng acc xshare. Hãy ủng hộ dangcaphd.com: tạo và nâng cấp VIP acc của bạn nhé!',30000)

def dangcaphd_get_page_control(body,mode,query):
	pattern='<a class="current">\d{1,5}</a><a href="(.+?)">(\d{1,5})</a>.*<a href=".+?page=(\d{1,5})">.+?</a></div>'
	page_control=re.search(pattern,body)
	if page_control:
		href=re.sub('&amp;','',xshare_group(page_control,1));trangke=xshare_group(page_control,2)
		tongtrang=int(xshare_group(page_control,3))/35+1
		name=color['trangtiep']+'Trang tiếp theo: trang %s/%d[/COLOR]'%(trangke,tongtrang)
		addir(name,href,mode=mode,query=query,isFolder=True)

def dangcaphd_get_cookie():
		name=myaddon.getSetting('mail_dchd')
		if not name:mess(u'Bạn hãy set acc dangcaphd cho plugin!');cookie=''
		else:cookie=myaddon.getSetting('cookie')
		return cookie

def dangcaphd_get_link(url):
	#hd['Cookie']=dangcaphd_get_cookie();body=make_request(url.replace('/movie-','/watch-'),headers=hd)
	#user=myaddon.getSetting('mail_dchd')
	#if user[:user.find('@')] not in body:
	hd['Cookie']=logindangcaphd()
	body=make_request(url.replace('/movie-','/watch-'),headers=hd)
	logoutdangcaphd(hd['Cookie'])
	return re.findall('"(\d{,3})" _link="(.+?)" _sub="(.*?)"',body)
	
def dangcaphd_download_sub(url):
	tempdir=mkdir_temp('temp')
	if not tempdir:return ''
	subfullpathfilename=os.path.join(tempdir,os.path.basename(url));sub=''
	if os.path.splitext(subfullpathfilename)[1] in [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass"]:
		if makerequest(subfullpathfilename,string=make_request(url),attr='wb'):sub=subfullpathfilename
	return sub

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

xbmcplugin.setContent(int(sys.argv[1]), 'movies')
params=get_params()
homnay=datetime.date.today().strftime("%d/%m/%Y")
url=name=fanart=img=date=query=end=''
mode=page=0;temp=[]

try:url=urllib.unquote_plus(params["url"])
except:pass
try:name=urllib.unquote_plus(params["name"])
except:pass
try:img=urllib.unquote_plus(params["img"])
except:pass
try:fanart=urllib.unquote_plus(params["fanart"])
except:pass
try:mode=int(params["mode"])
except:pass
try:page=int(params["page"])
except:pass
try:query=urllib.unquote_plus(params["query"])
except:pass#urllib.unquote
print "Main---------- Mode: "+str(mode),"URL: "+str(url),"Name: "+str(name),"query: "+str(query),"page: "+str(page)

if not mode:
	init_file();open_category("MMN");xbmcplugin.endOfDirectory(int(sys.argv[1]))
	data_download();data_update()
elif mode==2:end=google_search(url,query,mode,page)
elif mode==3:end=resolve_url(url)
elif mode==4:phimchon('http://vaphim.com','vaphim.xml','data="(.+?)" title')
elif mode==5:vp_xemnhieu()
elif mode==6:end=phimFshare(name,url,mode,page,query)
elif mode==7:end=fptplay(name,url,img,mode,page,query)
elif mode==8:hdvietnam(query,mode)
elif mode==9:make_mySearch(name,url,img,fanart,mode,query)
elif mode==10:open_category(query)
elif mode==11:make_myFshare(name,url,img,fanart,mode,query)
elif mode==12:make_mylist(name,url,img,fanart,mode,query)
elif mode==13:end=xshare_search(url,query,mode,page)
elif mode==15:end=id_2url(url,name,mode,page,query)
elif mode==16:end=play_maxspeed_link()
elif mode==17:end=megabox(name,url,mode,page,query)
elif mode==18:dangcaphd(name,url,img,mode,page,query)
elif mode==20:end=vp_update()
elif mode==31:end=ifile_update()
elif mode==34:phimchon("http://ifile.tv/phim","ifiletv.xml",'href=".+(\d{5}).+" class="mosaic-backdrop"')
elif mode==35:phimchon("http://ifile.tv/phim/index","ifiletv.xml",'href=".+(\d{5}).+" class="mosaic-backdrop"')
elif mode==38:doc_Trang4share(url)#38
elif mode==47:daklak47(name,url,img)
elif mode==90:end=doc_TrangFshare(url,img,fanart)
elif mode==91:main_menu(url,page,mode,query)
elif mode==94:end=subscene(name,url,query)
elif mode==95:lay_link_tenlua(url)
elif mode==96:end=doc_thumuccucbo(name,url,img,fanart,mode,query)
elif mode==97:doc_list_xml(url,name,page)
elif mode==98:make_favourites(name,url,img,fanart,mode,query)
elif mode==99:myaddon.openSettings();end='ok'
if not end or end not in 'no-ok':xbmcplugin.endOfDirectory(int(sys.argv[1]))
#https://urlfetch.readthedocs.org/en/v0.5.3/examples.html
#http://hdonline.vn/
#addir(name,url,img,fanart,mode,page,query,isFolder)
