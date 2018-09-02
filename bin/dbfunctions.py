#!/usr/bin/env python3
#! -*- coding: utf-8 -*-
import pymysql
import time
#from pymysql.constants.CLIENT import MULTI_STATEMENTS

host = 'localhost'
user = ''
password = ''
db = ''

""" Database Connection """

try:
  connection = pymysql.connect(
    host=host, 
    user=user, 
    password=password, 
    db=db, 
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor,
    client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
    )

  cursor = connection.cursor()

except ERROR as e:
 print('Got error {!r}, errno is {}'.format(e, e.args[0]))


""""""""""""""""""""""""
"""DATABASE FUNCTIONS"""
""""""""""""""""""""""""
def get_customers():
  sql = "SELECT customer_id, name FROM customers ORDER BY name"
  try:
    cursor.execute(sql)
    result = cursor.fetchall()
    return result
  except pymysql.InternalError:
    raise

def get_acl_details(customer):
  sql = """SELECT acl_id, customer_id, acl_name, acl_format, router, interface,
  max_lines, match_option, traffic_monitoring, sales_order, start_date
  FROM acl_details WHERE customer_id = %s"""
  try:
    cursor.execute(sql, (customer,))
    result = cursor.fetchall()
    return result
  except pymysql.InternalError:
    raise

def get_acl_details_for_db():
  sql = "SELECT acl_id, customer_id, acl_name, acl_format, router FROM acl_details"
  try:
    cursor.execute(sql)
    result = cursor.fetchall()
    return result
  except pymysql.InternalError:
    raise

def get_acls():
  sql = """SELECT acl_id, name, acl_name, acl_format, router, interface,
  max_lines, match_option, traffic_monitoring, sales_order, start_date
  FROM acl_details INNER JOIN customers ON acl_details.customer_id=customers.customer_id"""
  try:
    cursor.execute(sql)
    result = cursor.fetchall()
    return result
  except pymysql.InternalError:
    raise


def does_table_exist(name):
  sql = "SHOW TABLES LIKE %s"
  cursor.execute(sql, (name,))
  result = cursor.fetchone()
  return result

def create_cisco_table(name):
  sql = """CREATE TABLE IF NOT EXISTS `"""+name+ """` (
  id INT NOT NULL AUTO_INCREMENT,
  customer_id INT(11) NULL,
  sequence VARCHAR(11) NULL,
  statement VARCHAR(80) NULL,
  matches VARCHAR(8) NULL,
  date_taken DATETIME NULL, 
  PRIMARY KEY (id))"""
  try:
    cursor.execute(sql)
  except pymysql.InternalError as e:
    print('Got error {!r}, errno is {}'.format(e, e.args[0]))

def create_juniper_table(name):
  sql = """CREATE TABLE IF NOT EXISTS `"""+name+ """` (
  id INT NOT NULL AUTO_INCREMENT,
  customer_id INT(11) NULL,
  statement VARCHAR(200) NULL,
  date_taken DATETIME NULL,
  PRIMARY KEY(id))"""
  try:
    cursor.execute(sql)
  except pymysql.InternalError as e:
    print('Got error {!r}, errno is {}'.format(e, e.args[0]))

def create_juniper_matches_table(name):
  sql = """CREATE TABLE IF NOT EXISTS `"""+name+ """` (
  id INT NOT NULL AUTO_INCREMENT,
  acl_id INT(11) NOT NULL,
  customer_id INT(11) NOT NULL,
  term VARCHAR(100) NOT NULL,
  match_count INT(20) NOT NULL,
  date_taken DATETIME NULL,
  PRIMARY KEY(id)
  )"""
  try:
    cursor.execute(sql)
  except pymysql.InternalError as e:
    print('Got error {!r}, errno is {}'.format(e, e.args[0]))

def insert_juniper_acl(name, customer_id, statement):
  sql = """INSERT INTO `"""+name+ """` (
  `customer_id`, `statement`, `date_taken`
  ) VALUES (
  %s, %s, %s
  )
  """
  try:
    cursor.execute(sql, (customer_id, statement, time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
  except pymysql.InternalError as e:
    raise   

def insert_juniper_matches(table_name, acl_id, customer_id, term, packets):
  sql = """INSERT INTO `"""+table_name+"""` (
  `acl_id`, `customer_id`, `term`, `match_count`,  `date_taken`
  ) VALUES (%s, %s,%s, %s,%s)"""
  try:
    cursor.execute(sql, (acl_id, customer_id, term, packets, time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit
  except pymysql.InternalError as e:
    raise
    #print('Got error {!r}, errno is {}'.format(e, e.args[0]))

def insert_cisco_acl(name, customer_id, sequence, statement, matches):
  sql = """INSERT INTO `"""+name+"""` (
  `customer_id`, `sequence`, `statement`, `matches`, `date_taken`
  )
  VALUES (
  %s, %s, %s, %s, %s
  )"""
  try:
    cursor.execute(sql, (customer_id, sequence, statement, matches, time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
  except pymysql.InternalError as e:
    raise
  #print(name, type(customer_id), type(sequence), type(statement), type(matches))  

