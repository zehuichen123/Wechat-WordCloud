#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import requests
import re
from os import path
from PIL import Image
import numpy as np
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud,STOPWORDS

def get_catalogs(book_id):
	url='http://chushu.la/api/book/chushula-{0}?isAjax=1'.format(book_id)
	req=requests.get(url)
	menu_json=req.json()
	catalogs_info=menu_json['book']['catalogs']
	return catalogs_info

def get_each_posts(catalogs_info,book_id):
	url='http://chushu.la/api/book/wx/chushula-{0}/pages?isAjax=1'.format(book_id)
	headers={
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
		'Content-Type':'application/json'
	}
	index=2
	all_posts=[]
	for catalog in catalogs_info:
		year_num=catalog['year']
		month_num=catalog['month']
		index+=1
		form_data={
			"type":'year_month',
			"year": year_num,
	        "month": month_num,
	        "index": str(index),
	        "value": 'v_{0}{1}'.format(year_num, month_num)
		}
		req_posts=requests.post(url,json=form_data,headers=headers)
		req_json=req_posts.json()
		all_posts.append(req_json)
	return all_posts

def parse_json(all_posts):
	pattern=re.compile(u"[\u4e00-\u9fa5]+")
	parse_posts=[]
	all_posts_text=[]
	for each_json in all_posts:
		each_post_list=each_json['pages'][1:]
		for each_post in each_post_list:
			try:
				post_content=""
				save_text=""
				post_row=each_post['data']['paras'][0]['rows']
				for each_row in post_row:
					if type(each_row)==dict:
						save_text+=each_row['data']
						result = re.findall(pattern,each_row['data'])
						for each_word in result:
							post_content+=each_word
				parse_posts.append(post_content)
				all_posts_text.append(save_text)
			except Exception as e:
				pass
	return parse_posts,all_posts_text

def word_cloud(parse_posts):
	final_post_line=""
	mask_file_name=input('please input your mask file name,like favicon.png: ')
	for each_post in parse_posts:
		final_post_line+=each_post

	cut_texts=" ".join(jieba.cut(final_post_line))
	curr_path=path.abspath('.')
	font_path=path.join(curr_path,"simhei.ttf")
	your_mask=np.array(Image.open(path.join(curr_path,mask_file_name)))
	font_path=path.join(curr_path,"simhei.ttf")
	stopwords = set(STOPWORDS)
	stopwords.add("said")
	wc = WordCloud(background_color="white", max_words=2000, mask=your_mask,
               stopwords=stopwords,font_path=font_path)
	wc.generate(cut_texts)
	wc.to_file(path.join(curr_path,'wechat.png'))
	plt.imshow(wc,interpolation='bilinear')
	plt.axis("off")
	plt.show()

def save_posts_text(all_posts_text):
	for i,each_post in enumerate(all_posts_text):
		remove_start_list=[]
		remove_end_list=[]
		remove_character=False
		for index,each_character in enumerate(each_post):
			if each_character=='<':
				remove_start_list.append(index)
				remove_character=True
			elif each_character=='>':
				remove_end_list.append(index)
		if remove_character==True:
			final_list=""
			prev_end_index=0
			for start_index,end_index in zip(remove_start_list,remove_end_list):
				final_list+=each_post[prev_end_index:start_index]
				prev_end_index=end_index+1
			all_posts_text[i]=final_list
	with open('wechat.txt','w') as f:
		for each_post in all_posts_text:
			f.write(each_post)
			f.write('\n')
	return

bookid=str(input('please input your bookid:'))
catalogs=get_catalogs(bookid)
print('catalogs got')
all_posts=get_each_posts(catalogs,bookid)
print('all_posts got')
parse_posts,all_posts_text=parse_json(all_posts)
print('parse finished')
y_n=input('whether save your posts into wechat.txt?(y/n): ')
if y_n=='y':
	save_posts_text(all_posts_text)
word_cloud(parse_posts)