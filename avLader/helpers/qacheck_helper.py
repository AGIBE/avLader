# -*- coding: utf-8 -*-
from __future__ import division
import os
from datetime import datetime as dt
import avLader.helpers.sql_helper
import avLader.helpers.excel_writer

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
	
	conn_vek2 = "host='" + config['GEODB_VEK2_PG']['host'] + "' dbname='" + config['GEODB_VEK2_PG']['database'] + "' port ='" + config['GEODB_VEK2_PG']['port'] + "' user='" + config['GEODB_VEK2_PG']['username'] + "' password='" + config['GEODB_VEK2_PG']['password'] + "'"
	conn_norm = "host='" + config['NORM_TEAM_PG']['host'] + "' dbname='" + config['NORM_TEAM_PG']['database'] + "' port ='" + config['NORM_TEAM_PG']['port'] + "' user='" + config['NORM_TEAM_PG']['username'] + "' password='" + config['NORM_TEAM_PG']['password'] + "'"


	# Get Ebene pro GPRCODE
	sql_get_ebe_current = "SELECT geodb_dd.tb_geoprodukt.gpr_bezeichnung || '_'||  geodb_dd.tb_ebene.ebe_bezeichnung FROM  geodb_dd.tb_geoprodukt  INNER JOIN geodb_dd.tb_geoprodukt_zeitstand ON geodb_dd.tb_geoprodukt.gpr_objectid = geodb_dd.tb_geoprodukt_zeitstand.gpr_objectid  AND geodb_dd.tb_geoprodukt_zeitstand.gzs_objectid = geodb_dd.tb_geoprodukt.gzs_objectid INNER JOIN geodb_dd.tb_ebene_zeitstand ON geodb_dd.tb_geoprodukt_zeitstand.gzs_objectid = geodb_dd.tb_ebene_zeitstand.gzs_objectid  INNER JOIN geodb_dd.tb_ebene ON geodb_dd.tb_ebene.ebe_objectid = geodb_dd.tb_ebene_zeitstand.ebe_objectid WHERE GPR_BEZEICHNUNG = '" + gp + "' ORDER BY  geodb_dd.tb_geoprodukt.gpr_bezeichnung"
	
	# Ebenen zu GP auslesen
	ebe_current = avLader.helpers.sql_helper.readSQL(config['GEODB_DD_TEAM']['connection_string'], sql_get_ebe_current)

	ebenen = ebe_current

	# Tab Ebene vorbereiten:
	tab_ebe = gp + "_COUNT"

	#Header schreiben
	title = ["Ebene", "Count vek2","Count Norm","Change %","Area","Attribut","Wert"]
	width = [25, 20, 20, 15, 15, 15, 60]
	avLader.helpers.excel_writer.tab_write_header(tab_ebe, title, width)
	n=1
	for ebene in ebenen:
		ebene = ebene[0]
		# Anzahl Datensätze vergleichen
		logger.info('Vergleiche Ebene ' + ebene)
		# Get Anzahl von vek2p
		try:
			if quelle_pg is True:
				sql = 'SELECT count(*) FROM geodb.' + ebene.lower()
				count_vek2 = avLader.helpers.sql_helper.readSQL_PG(logger, conn_vek2, sql, fetch=True, fetchall=False)
			else:
				sql = 'SELECT count(*) FROM GEODB.' + ebene.upper()
				count_vek2 = avLader.helpers.sql_helper.readSQL(config['GEODB_VEK2']['connection_string'], sql)
				count_vek2 = count_vek2[0][0]
		except Exception as e:
			logger.warn(e)
			count_vek2 = 0
		# Get Anzahl von norm
		try:
			if quelle_pg is True:
				sql = 'SELECT count(*) FROM norm.' + ebene.lower()
				count_norm = avLader.helpers.sql_helper.readSQL_PG(logger, conn_norm, sql, fetch=True, fetchall=False)
			else:
				sql = 'SELECT count(*) FROM NORM.' + ebene.upper()
				count_norm = avLader.helpers.sql_helper.readSQL(config['NORM_TEAM']['connection_string'], sql)
				count_norm = count_norm[0][0]
		except Exception as e:
			logger.warn(e)
			count_norm = 0
	
		#Div by zero verhindern:
		if(count_norm == 0 or count_norm is None) and count_vek2 == 0:
			division = 0
		elif count_norm == 0 or count_norm is None:
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
			avLader.helpers.excel_writer.tab_write_data(tab_ebe, line_feature, n)
		else:
			logger.info("Total vek2: " + str(count_vek2))
			logger.info("Total Norm: " + str(count_norm))
			#Daten schreiben Ebenen:
			avLader.helpers.excel_writer.tab_write_data_warn(tab_ebe, line_feature, n)
	
		if gemeinde is True:
			logger.info("Vergleiche Gemeinden: " + ebene)
			if quelle_pg is True:
				sql = "SELECT udt_name FROM information_schema.columns WHERE table_schema = 'geodb' AND table_name like '" + ebene.lower() + "' AND udt_name like 'geometry'"
				preselct_vek2 = avLader.helpers.sql_helper.readSQL_PG(logger, conn_vek2, sql, fetch=True)
				sql = "SELECT udt_name FROM information_schema.columns WHERE table_schema = 'norm' AND table_name like '" + ebene.lower() + "' AND udt_name like 'geometry'"
				preselct_norm = avLader.helpers.sql_helper.readSQL_PG(logger, conn_norm, sql, fetch=True)
			else:
				sql = "SELECT TABLE_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = 'GEODB' and TABLE_NAME LIKE '" + ebene.upper() + "' and DATA_TYPE LIKE '%GEOM%'"
				preselct_vek2 = avLader.helpers.sql_helper.readSQL(config['GEODB_VEK2']['connection_string'], sql)
				sql = "SELECT TABLE_NAME FROM ALL_TAB_COLUMNS WHERE OWNER = 'NORM' and TABLE_NAME LIKE '" + ebene.upper() + "' and DATA_TYPE LIKE '%GEOM%'"
				preselct_norm = avLader.helpers.sql_helper.readSQL(config['NORM_TEAM']['connection_string'], sql)
			if preselct_norm is not None and quelle_pg is False:
				preselct_norm = preselct_norm[0]
			if preselct_vek2 is not None and quelle_pg is False:
				preselct_vek2 = preselct_vek2[0]
	
			if preselct_vek2 is not None and preselct_norm is not None:
				# Get Anzahl von vek2p & Norm
				if quelle_pg is True:
					sql = 'SELECT grenz5_g5.gmde, count(grenz5_g5.gmde) FROM geodb.grenz5_g5 LEFT JOIN geodb.' + ebene.lower() + ' ON st_intersects(grenz5_g5.shape, ' + ebene.lower() + '.shape) group by grenz5_g5.gmde'
					count_vek2 = avLader.helpers.sql_helper.readSQL_PG(logger, conn_vek2, sql, fetch=True, fetchall=True)
					sql = 'SELECT grenz5_g5.gmde, count(grenz5_g5.gmde) FROM norm.grenz5_g5 LEFT JOIN norm.' + ebene.lower() + ' ON st_intersects(grenz5_g5.shape, '  + ebene.lower() + '.shape) group by grenz5_g5.gmde'
					count_norm = avLader.helpers.sql_helper.readSQL_PG(logger, conn_norm, sql, fetch=True, fetchall=True)
				else:
					sql = 'SELECT grenz5_g5.gmde, count(grenz5_g5.gmde) FROM GEODB.GRENZ5_G5, GEODB.' + ebene.upper() + ' where sde.st_intersects(grenz5_g5.shape, ' + ebene.upper() + '.shape) = 1 group by grenz5_g5.gmde'
					count_vek2 = avLader.helpers.sql_helper.readSQL(config['GEODB_VEK2']['connection_string'], sql)
					sql = 'SELECT grenz5_g5.gmde, count(grenz5_g5.gmde) FROM NORM.GRENZ5_G5, NORM.' + ebene.upper() + ' where sde.st_intersects(grenz5_g5.shape, ' + ebene.upper() + '.shape) = 1 group by grenz5_g5.gmde'
					count_norm = avLader.helpers.sql_helper.readSQL(config['NORM_TEAM']['connection_string'], sql)
	
				if count_norm is None and quelle_pg is False:
					logger.warn("Keine Features fuer NORM_VIEWER gefunden. Rechte auf Features im ArcCatalog -> Manage -> Privileges vergeben.")
				elif count_norm is None and quelle_pg is True:
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
							avLader.helpers.excel_writer.tab_write_data(tab_ebe, line_gem, n)
						else:
							#Daten schreiben Ebenen:
							avLader.helpers.excel_writer.tab_write_data_warn(tab_ebe, line_gem, n)
			else:
				logger.warn("Keine georeferenzierte Abfrage der Gemeinden moeglich.")
	
		# Anzahl Datensätze gruppiert nach Attribut vergleichen
		for attr in attr_group:
			try:
				if quelle_pg is True:
					sql = 'SELECT ' + attr + ', count(*) from geodb.' + ebene.lower() + ' group by ' + attr + ' order by ' + attr
					count_vek2 = avLader.helpers.sql_helper.readSQL_PG(logger, conn_vek2, sql, fetch=True, fetchall=False)
					sql = 'SELECT ' + attr + ', count(*) from norm.' + ebene.lower() + ' group by ' + attr + ' order by ' + attr
					count_norm = avLader.helpers.sql_helper.readSQL_PG(logger, conn_norm, sql, fetch=True, fetchall=False)
				else:
					sql = 'SELECT ' + attr + ', count(*) from GEODB.' + ebene.upper() + ' group by ' + attr + ' order by ' + attr
					count_vek2 = avLader.helpers.sql_helper.readSQL(config['GEODB_VEK2']['connection_string'], sql)
					sql = 'SELECT ' + attr + ', count(*) from NORM.' + ebene.upper() + ' group by ' + attr + ' order by ' + attr
					count_norm = avLader.helpers.sql_helper.readSQL(config['NORM_TEAM']['connection_string'], sql)
	
				# Linie schreiben
				if (count_norm is None or count_norm == []) and (count_vek2 is None or count_vek2 == []):
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
							avLader.helpers.excel_writer.tab_write_data(tab_ebe, line_attr, n)
						else:
							#Daten schreiben Ebenen:
							avLader.helpers.excel_writer.tab_write_data_warn(tab_ebe, line_attr, n)
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
								avLader.helpers.excel_writer.tab_write_data_warn(tab_ebe, line_attr, n)
						else:
							pass
			except Exception as e:
				logger.warn(e)
				pass

	# Excel speichern
	now = dt.now()
	out_file = os.path.join(config['LOGGING']['log_directory'], gp + "_count_features_" + now.strftime("%Y%m%d%H%M%S") +".xlsx")
	avLader.helpers.excel_writer.save_excel(out_file)
	logger.info("Check-Resultate wurden in Excel-File geschrieben: " + out_file)
