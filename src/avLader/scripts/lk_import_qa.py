# -*- coding: utf-8 -*-
from __future__ import division
import AGILib.connection
import AGILib.excel_writer
import os
import psycopg2
from datetime import datetime as dt


def check_count_features(config, logger, gp, attr_group = [], quelle_pg = False, gemeinde = False, lower_bound = -2.0, upper_bound = 10.0):
	'''
	Script zum Vergleichen der Anzahl Features pro Ebene zwischen Norm und Vek2.
	Vergleich der Anzahl Features pro Attribut-Werte und Ebene möglich. 
	Vergleich der Anzahl Features pro Gemeinde und Ebene möglich.
	ACHTUNG: Vergleich pro Gemeinde sollte aus Performance-Gründen auf der PostGIS-DB gemacht werden.
	:param config: config
	:param logger: log-Objekt
	:param gp: Der Code des Geoprodukts
	:param quelle_pg: Vergleich findet auf PostGIS-DB statt
	:param attr_group: Liste der zu vergleichenden Attribute
	:param gemeinde: Vergleich findet pro Gemeinde statt
	:param lower_bound: Untere Toleranzgrenze für Warnungen
	:param upper_bound: Obere Toleranzgrenze für Warnungen
	'''
	
	logger.info("Der QA-Check Count Features wird gestartet. GPRCODE: " + gp)

	ew = AGILib.excel_writer.ExcelWriter()
	
	# Get Ebene pro GPRCODE
	sql_get_ebe_current = "SELECT geodb_dd.tb_geoprodukt.gpr_bezeichnung || '_'||  geodb_dd.tb_ebene.ebe_bezeichnung FROM  geodb_dd.tb_geoprodukt  INNER JOIN geodb_dd.tb_geoprodukt_zeitstand ON geodb_dd.tb_geoprodukt.gpr_objectid = geodb_dd.tb_geoprodukt_zeitstand.gpr_objectid  AND geodb_dd.tb_geoprodukt_zeitstand.gzs_objectid = geodb_dd.tb_geoprodukt.gzs_objectid INNER JOIN geodb_dd.tb_ebene_zeitstand ON geodb_dd.tb_geoprodukt_zeitstand.gzs_objectid = geodb_dd.tb_ebene_zeitstand.gzs_objectid  INNER JOIN geodb_dd.tb_ebene ON geodb_dd.tb_ebene.ebe_objectid = geodb_dd.tb_ebene_zeitstand.ebe_objectid WHERE GPR_BEZEICHNUNG = '" + gp + "' ORDER BY  geodb_dd.tb_geoprodukt.gpr_bezeichnung"
	
	# Ebenen zu GP auslesen
	ebe_current = config['GEODB_DD_TEAM']['connection'].db_read(sql_get_ebe_current)

	ebenen = ebe_current

	# Tab Ebene vorbereiten:
	tab_ebe = gp + "_COUNT"

	#Header schreiben
	title = ["Ebene", "Count vek2","Count Norm","Change %","Area","Attribut","Wert"]
	width = [25, 20, 20, 15, 15, 15, 60]
	ew.tab_write_header(tab_ebe, title, width)
	n=1
	for ebene in ebenen:
		ebene = ebene[0]
		# Anzahl Datensätze vergleichen
		logger.info('Vergleiche Ebene ' + ebene)
		# Get Anzahl von vek2p
		try:
			if quelle_pg is True:
				conn = config['GEODB_VEK2_PG']['connection']
			else:
				conn = config['GEODB_VEK2']['connection']
			sql = 'SELECT count(*) FROM geodb.' + ebene.lower()
			count_vek2 = conn.db_read(sql)[0][0]
		except Exception as e:
			logger.warn(e)
			count_vek2 = 0
		# Get Anzahl von norm
		try:
			if quelle_pg is True:
				conn = config['NORM_TEAM_PG']['connection']
			else:
				conn = config['NORM_TEAM']['connection']
			sql = 'SELECT count(*) FROM norm.' + ebene.lower()
			count_norm = conn.db_read(sql)[0][0]
		except Exception as e:
			logger.warn(e)
			count_norm = 0
	
		#Div by zero verhindern:
		if(count_norm == 0 or count_norm is None) and count_vek2 == 0:
			division = 0
		elif count_norm == 0 or count_norm is None or count_vek2 == 0:
			division = -100
		else:
			division = 100*count_norm/count_vek2-100
		area = "BE"
		attribute = "None"
		wert = "None"
		if count_norm is None:
			count_norm = "missing"
		if count_vek2 is None:
			count_vek2 = "missing"
		line_feature = []
		line_feature.extend([ebene,count_vek2, count_norm, division,area,attribute,wert])
		n = n+1
		if lower_bound < division < upper_bound:
			logger.info("Total vek2: " + str(count_vek2))
			logger.info("Total Norm: " + str(count_norm))
			#Daten schreiben Ebenen:
			ew.tab_write_data(tab_ebe, line_feature, n)
		else:
			logger.info("Total vek2: " + str(count_vek2))
			logger.info("Total Norm: " + str(count_norm))
			#Daten schreiben Ebenen:
			ew.tab_write_data_warn(tab_ebe, line_feature, n)
	
		if gemeinde is True:
			logger.info("Vergleiche Gemeinden: " + ebene)
			if quelle_pg is True:
				sql = "SELECT udt_name FROM information_schema.columns WHERE table_schema = 'geodb' AND table_name like '" + ebene.lower() + "' AND udt_name like 'geometry'"
				preselct_vek2 = config['GEODB_VEK2_PG']['connection'].db_read(sql)
				sql = "SELECT udt_name FROM information_schema.columns WHERE table_schema = 'norm' AND table_name like '" + ebene.lower() + "' AND udt_name like 'geometry'"
				preselct_norm = config['NORM_TEAM_PG']['connection'].db_read(sql)
			else:
				sql = "SELECT TABLE_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = 'GEODB' and TABLE_NAME LIKE '" + ebene.upper() + "' and DATA_TYPE LIKE '%GEOM%'"
				preselct_vek2 = config['GEODB_VEK2']['connection'].db_read(sql)
				sql = "SELECT TABLE_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = 'NORM' and TABLE_NAME LIKE '" + ebene.upper() + "' and DATA_TYPE LIKE '%GEOM%'"
				preselct_norm = config['NORM_TEAM']['connection'].db_read(sql)
			if preselct_norm is not None and quelle_pg is False:
				preselct_norm = preselct_norm[0]
			if preselct_vek2 is not None and quelle_pg is False:
				preselct_vek2 = preselct_vek2[0]
	
			if len(preselct_vek2) > 0 and len(preselct_norm) > 0:
				# Get Anzahl von vek2p & Norm
				if quelle_pg is True:
					try:
						sql = 'SELECT grenz5_g5.bfsnr, count(grenz5_g5.bfsnr) FROM geodb.grenz5_g5 LEFT JOIN geodb.' + ebene.lower() + ' ON st_intersects(grenz5_g5.shape, ' + ebene.lower() + '.shape) group by grenz5_g5.bfsnr'
						count_vek2 =  config['GEODB_VEK2_PG']['connection'].db_read(sql)
						sql = 'SELECT grenz5_g5.bfsnr, count(grenz5_g5.bfsnr) FROM norm.grenz5_g5 LEFT JOIN norm.' + ebene.lower() + ' ON st_intersects(grenz5_g5.shape, '  + ebene.lower() + '.shape) group by grenz5_g5.bfsnr'
						count_norm = config['NORM_TEAM_PG']['connection'].db_read(sql)
					except psycopg2.Error as e:
						logger.warn("Die PostGIS-Abfrage hat einen Fehler zurückgegeben.")
						logger.warn(e.pgerror)
						logger.warn(e.cursor.query)
						count_norm = ""
				else:
					sql = 'SELECT grenz5_g5.bfsnr, count(grenz5_g5.bfsnr) FROM GEODB.GRENZ5_G5, GEODB.' + ebene.upper() + ' where sde.st_intersects(grenz5_g5.shape, ' + ebene.upper() + '.shape) = 1 group by grenz5_g5.bfsnr'
					count_vek2 = config['GEODB_VEK2']['connection'].db_read(sql)
					sql = 'SELECT grenz5_g5.bfsnr, count(grenz5_g5.bfsnr) FROM NORM.GRENZ5_G5, NORM.' + ebene.upper() + ' where sde.st_intersects(grenz5_g5.shape, ' + ebene.upper() + '.shape) = 1 group by grenz5_g5.bfsnr'
					count_norm = config['NORM_TEAM']['connection'].db_read(sql)
	
				if len(count_norm) == 0 and quelle_pg is False:
					logger.warn("Keine Features fuer NORM_VIEWER gefunden. Rechte auf Features im ArcCatalog -> Manage -> Privileges vergeben.")
				elif len(count_norm) == 0 and quelle_pg is True:
					logger.warn("Keine Features auf TEAM PostGIS gefunden.")
				else:
					# Linie schreiben
					for value in count_vek2:
						attribute = "None"
						wert = "None"
						line_gem = []
						line_gem.append(ebene)
						line_gem.append(value[1])
						# Entsprechende Wert in norm
						value_norm = [item for item in count_norm if item[0] == value[0]]
						if value_norm == []:
							value_norm = [(value[0], 0)]
						line_gem.append(value_norm[0][1])
						divison_gem = 100*value_norm[0][1]/value[1]-100
						line_gem.append(divison_gem)
						line_gem.append(value[0])
						line_gem.append(attribute)
						line_gem.append(wert)
						#Daten schreiben Gemeinden:
						n=n+1
						if lower_bound < divison_gem < upper_bound:
							#Daten schreiben Ebenen:
							ew.tab_write_data(tab_ebe, line_gem, n)
						else:
							#Daten schreiben Ebenen:
							ew.tab_write_data_warn(tab_ebe, line_gem, n)
			else:
				logger.warn("Keine georeferenzierte Abfrage der Gemeinden moeglich.")
	
		# Anzahl Datensätze gruppiert nach Attribut vergleichen
		for attr in attr_group:
			try:
				if quelle_pg is True:
					sql = 'SELECT ' + attr + ', count(*) from geodb.' + ebene.lower() + ' group by ' + attr + ' order by ' + attr
					count_vek2 = config['GEODB_VEK2_PG']['connection'].db_read(sql)
					sql = 'SELECT ' + attr + ', count(*) from norm.' + ebene.lower() + ' group by ' + attr + ' order by ' + attr
					count_norm = config['TEAM_NORM_PG']['connection'].db_read(sql)
				else:
					sql = 'SELECT ' + attr + ', count(*) from GEODB.' + ebene.upper() + ' group by ' + attr + ' order by ' + attr
					count_vek2 = config['GEODB_VEK2']['connection'].db_read(sql)
					sql = 'SELECT ' + attr + ', count(*) from NORM.' + ebene.upper() + ' group by ' + attr + ' order by ' + attr
					count_norm = config['NORM_TEAM']['connection'].db_read(sql)
	
				# Linie schreiben
				if len(count_norm) == 0 and len(count_vek2) == 0:
					logger.warn("Keine Abfrage des Attributs '" + attr + "' moeglich.")
				else:
					logger.warn("Vergleiche Attribute: " + attr)
					for value in count_vek2:
						line_attr = []
						line_attr.append(ebene)
						line_attr.append(value[1])
						# Entsprechende Wert in norm
						value_norm = [item for item in count_norm if item[0] == value[0]]
						if value_norm == []:
							value_norm = [(value[0], 0)]
						line_attr.append(value_norm[0][1])
						divison_attr =100*value_norm[0][1]/value[1]-100
						line_attr.append(divison_attr)
						line_attr.append("BE")
						line_attr.append(attr)
						line_attr.append(value[0])
						#Daten schreiben Attribute:
						n=n+1
						if lower_bound < divison_attr < upper_bound:
							#Daten schreiben Ebenen:
							ew.tab_write_data(tab_ebe, line_attr, n)
						else:
							#Daten schreiben Ebenen:
							ew.tab_write_data_warn(tab_ebe, line_attr, n)
					for value in count_norm:
						line_attr = []
						if not [item for item in count_vek2 if item[0] == value[0]]:
							line_attr.append(ebene)
							line_attr.append('missing')
							line_attr.append(value[1])
							line_attr.append(100)
							line_attr.append("BE")
							line_attr.append(attr)
							line_attr.append(value[0])
							if line_attr is []:
								pass
							else:
								n=n+1
								ew.tab_write_data_warn(tab_ebe, line_attr, n)
						else:
							pass
			except Exception as e:
				logger.warn(e)
				pass

	# Excel speichern
	now = dt.now()
	out_file = os.path.join(config['LOGGING']['log_directory'], gp + "_count_features_" + now.strftime("%Y%m%d%H%M%S") +".xlsx")
	ew.save_xlsx(out_file)
	logger.info("Check-Resultate wurden in Excel-File geschrieben: " + out_file)
