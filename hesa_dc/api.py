# Copyright (c) 2022, Sitenet and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def get_all_hesa_returns():
	#import os
	#file_path = '{0}/hesa_return'.format(frappe.get_site_path('private', 'files'))
	#xml_list = []
	#if os.path.exists(file_path):
	#	for filename in os.listdir(file_path):
	#		if filename.endswith(".xml"):
	#			xml_list.append(filename)
	#return xml_list

	##Reading from doctype instead of private directory
	hesa_histories = frappe.db.sql('''SELECT `return_type`,`name`,`creation`,`file_link` FROM `tabHESA DC Return History` ORDER BY `creation` DESC LIMIT 10''')
	#return hesa_histories
	html_table = '''<tr><th>Return Type</th><th>File Name</th><th>Created at</th><th class="text-center">Download</th><th class="text-center">Delete</th></tr>'''
	inner_table = ''
	for history in hesa_histories:
		inner_table = inner_table + '''<tr><td>%s</td>'''%history[0]
		inner_table = inner_table + '''<td>%s</td>'''%history[1]
		inner_table = inner_table + '''<td>%s</td>'''%history[2].strftime("%Y-%m-%d, %H:%M:%S")
		inner_table = inner_table + '''<td class="text-center"><a href="#" class="download" data-filename="%s"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 15v4c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2v-4M17 9l-5 5-5-5M12 12.8V2.5"/></svg></a></td>'''%history[3]
		inner_table = inner_table + '''<td class="text-center"><a href="#" class="delete" data-filename="%s"><svg class="icon  icon-sm" style=""><use class="" href="#icon-delete"></use></svg></a></td></tr>'''%history[3]

	table = '''<table class="table table-hover">'''+html_table+inner_table
	table = table + '''</table>'''
	return table

@frappe.whitelist()
def get_hesa_returns_data(file_name):
	import os
	import xml.dom.minidom
	#file_path = '{0}/hesa_return/{1}'.format(frappe.get_site_path('private', 'files'),file_name)
	dom = xml.dom.minidom.parse(file_name)
	xml_as_string = dom.toxml()
	return xml_as_string


@frappe.whitelist()
def delete_hesa_return_file(file_name):
	import os
	file_path = file_name
	frappe.delete_doc('HESA DC Return History', file_name.split('/')[-1])
	os.remove(file_path)
	return True


@frappe.whitelist()
def create_hesa_dc_sa_return_file(returnType, submissionPurpose, academicYear=2021, academicTerm=None):
    import os
    from datetime import datetime
    QUALENT3_List = ['P41', 'P42', 'P46', 'P47', 'P50', 'P51', 'P53', 'P54', 'P62', 'P63', 'P64', 'P65', 'P68', 'P93', 'P94', 'X00', 'X01']
    DOMICILE_List = ['XF', 'XG', 'XH', 'XI', 'XK', 'XL', 'GG', 'JE', 'IM']
    today = datetime.now()
    directory_path = frappe.get_site_path('private','files')
    directory_exists = os.path.exists('{0}/hesa_return'.format(directory_path))
    session = academicYear.split('-')[0][-2:]
    if not directory_exists:
        os.makedirs('{0}/hesa_return'.format(directory_path))
    file_exists =  os.path.exists('{0}/hesa_return/{1}-HESA-{2}.xml'.format(directory_path,str(session+company_data['recid']),int(datetime.timestamp(today))))
    if file_exists:
        return False
    doc = frappe.new_doc('HESA DC Return History')
    from xml.dom import minidom
        
    company_data = frappe.db.sql('''SELECT recid, ukprn FROM tabHESA DC Student Alternative WHERE label = "%s"'''%returnType, as_dict=1)[0]
    all_course_data = frappe.db.sql('''SELECT * FROM tabCourse''',as_dict=1)
    all_student_data = frappe.db.sql('''SELECT * FROM tabStudent''',as_dict=1)

    root = minidom.Document()

    #<APStudentRecord>
    ap_student_record = root.createElement('APStudentRecord')
    root.appendChild(ap_student_record)

    #<Provider>
    provider = root.createElement('Provider')
    ap_student_record.appendChild(provider)

    #<RECID>
    recid = root.createElement('RECID')
    recid.appendChild(root.createTextNode(company_data['recid']))
    provider.appendChild(recid)

    #<UKPRN>
    ukprn = root.createElement('UKPRN')
    ukprn.appendChild(root.createTextNode(company_data['ukprn']))
    provider.appendChild(ukprn)

    for course_data in all_course_data:
        #<Course>
        course = root.createElement('Course')
        provider.appendChild(course)

        #<COURSEID>
        course_id = root.createElement('COURSEID')
        course_id.appendChild(root.createTextNode(str(course_data.get('courseid','0'))))
        course.appendChild(course_id)

        #<OWNCOURSEID>
        if course_data.get('owncourseid', None) is not None:
            own_course_id = root.createElement('OWNCOURSEID')
            own_course_id.appendChild(root.createTextNode(str(course_data.get('owncourseid'))))
            course.appendChild(own_course_id)

        ##TODO Awarding body

        #<COURSEAIM>
        course_aim = root.createElement('COURSEAIM')
        course_aim.appendChild(root.createTextNode(course_data.get('course_aim','')))### Change according to database design
        course.appendChild(course_aim)

        #<CTITLE>
        course_title = root.createElement('CTITLE')
        course_title.appendChild(root.createTextNode(course_data.get('course_title','')))
        course.appendChild(course_title)

        #<REGBODY>
        if course_data.get('reg_body', None) is not None:
            reg_body = root.createElement('REGBODY')
            reg_body.appendChild(root.createTextNode(course_data.get('reg_body')))
            course.appendChild(reg_body)

        #<TTCID>
        ttcid = root.createElement('TTCID')
        ttcid.appendChild(root.createTextNode(str(course_data.get('ttcid','1'))))
        course.appendChild(ttcid)
        ##TODO update topic according to how the fields are designed later

        course_topics = frappe.db.sql('''SELECT * FROM `tabCourse Topic` WHERE parent="%s"''' % course_data.get('course_name'),as_dict=1)
        for topic in course_topics:
            #<CourseSubject>
            course_subject = root.createElement('CourseSubject')
            course.appendChild(course_subject)

            ##TODO sbjca change into topic code
            #<SBJCA>
            topic_sbjca = root.createElement('SBJCA')
            topic_sbjca.appendChild(root.createTextNode(topic.get('topic_name','')))
            course_subject.appendChild(topic_sbjca)

            #<SBJPCNT>
            topic_sbjpcnt = root.createElement('SBJPCNT')
            topic_sbjpcnt.appendChild(root.createTextNode(str(int(topic.get('sbjpcnt','100')))))
            course_subject.appendChild(topic_sbjpcnt)

        for del_org_loc in course_data.get('delivery_organisation_and_location',''):

            #<DeliveryOrganisationAndLocation>
            delivery_organisation_location = root.createElement('DeliveryOrganisationAndLocation')
            course.appendChild(delivery_organisation_location)

            #<DELORG>
            delorg = root.createElement('DELORG')
            delorg.appendChild(root.createTextNode(del_org_loc.get('delorg','')))
            delivery_organisation_location.appendChild(delorg)

            # #<DELORGPROP>
            # delorgprop = root.createElement('DELORGPROP')
            # delorgprop.appendChild(root.createTextNode(del_org_loc.get('delorgprop','')))
            # delivery_organisation_location.appendChild(delorgprop)

            #<PCODELOC>
            if del_org_loc.get('pcodeloc', None) is not None:
                pcodeloc = root.createElement('PCODELOC')
                pcodeloc.appendChild(root.createTextNode(del_org_loc.get('pcodeloc','')))
                delivery_organisation_location.appendChild(pcodeloc)

            
    #<Student>
    for student_data in all_student_data:
        student = root.createElement('Student')
        provider.appendChild(student)

        #<HUSID>
        husid = root.createElement('HUSID')
        husid.appendChild(root.createTextNode(str(student_data.get('husid',''))))
        student.appendChild(husid)

        #<OWNSTU>
        ownstu = root.createElement('OWNSTU')
        ownstu.appendChild(root.createTextNode(str(student_data.get('ownstu',''))))
        student.appendChild(ownstu)

        #<BIRTHDTE>
        birthdte = root.createElement('BIRTHDTE')
        if student_data.get('date_of_birth',None) is not None:
            birthdte.appendChild(root.createTextNode(str(student_data.get('date_of_birth',''))))
        student.appendChild(birthdte)

        #<FNAMES>
        fnames = root.createElement('FNAMES')
        if student_data.get('first_name',None) is not None:
            fore_name = student_data.get('first_name')
            if student_data.get('middle_name',None) is not None:
                fore_name = fore_name +' '+student_data.get('middle_name','')
            fnames.appendChild(root.createTextNode(fore_name))
        student.appendChild(fnames)

        #<SSN>
        if student_data.get('ssn',None) is not None:
            ssn = root.createElement('SSN')
            ssn.appendChild(root.createTextNode(str(student_data.get('ssn',''))))
            student.appendChild(ssn)

        #<SURNAME>
        surname = root.createElement('SURNAME')
        if student_data.get('last_name',None) is not None:
            surname.appendChild(root.createTextNode(student_data.get('last_name','')))
        student.appendChild(surname)

        #<UCASPERID>
        if student_data.get('ucasperid',None) is not None:
            ucasperid = root.createElement('UCASPERID')
            ucasperid.appendChild(root.createTextNode(str(student_data.get('ucasperid',''))))
            student.appendChild(ucasperid)

        #<ULN>
        if student_data.get('uln',None) is not None:
            uln = root.createElement('uln')
            uln.appendChild(root.createTextNode(str(student_data.get('uln',''))))
            student.appendChild(uln)

        #<EntryProfile>
        entry_profile = root.createElement('EntryProfile')
        student.appendChild(entry_profile)

        #<NUMHUS>
        numhus = root.createElement('NUMHUS')
        numhus.appendChild(root.createTextNode(str(student_data.get('numhus',''))))
        entry_profile.appendChild(numhus)

        #<CARELEAVER>
        if student_data.get('careleaver',None) is not None:
            careleaver = root.createElement('CARELEAVER')
            careleaver.appendChild(root.createTextNode(str(student_data.get('careleaver',''))))
            entry_profile.appendChild(careleaver)

        #<DOMICILE>
        if student_data.get('domicile',None) is not None:
            domicile = root.createElement('DOMICILE')
            domicile.appendChild(root.createTextNode(str(student_data.get('careleaver',''))))
            entry_profile.appendChild(domicile)

        #<POSTCODE>
        if student_data.get('postcode',None) is not None:
            postcode = root.createElement('POSTCODE')
            postcode.appendChild(root.createTextNode(str(student_data.get('postcode',''))))
            entry_profile.appendChild(postcode)

        #<PREVINST>
        if student_data.get('previnst',None) is not None:
            previnst = root.createElement('PREVINST')
            previnst.appendChild(root.createTextNode(str(student_data.get('previnst',''))))
            entry_profile.appendChild(previnst)

        #<QUALENT3>
        if student_data.get('qualent3',None) is not None:
            qualent3 = root.createElement('QUALENT3')
            qualent3.appendChild(root.createTextNode(str(student_data.get('qualent3',''))))
            entry_profile.appendChild(qualent3)

        if student_data.get('domicile',None) is not None and student_data.get('qualent3',None) is not None:
            if student_data.get('domicile') in DOMICILE_List and student_data.get('qualent3') in QUALENT3_List:
                #<QualificationsOnEntry>
                qualification_on_entry = root.createElement('QualificationsOnEntry')
                entry_profile.appendChild(qualification_on_entry)

                #<OWNQUAL>
                if student_data.get('ownqual',None) is not None:
                    ownqual = root.createElement('OWNQUAL')
                    ownqual.appendChild(root.createTextNode(str(student_data.get('ownqual',''))))
                    qualification_on_entry.appendChild(ownqual)

                #<QUALGRADE>
                if student_data.get('qualgrade',None) is not None:
                    qualgrade = root.createElement('QUALGRADE')
                    qualgrade.appendChild(root.createTextNode(str(student_data.get('qualgrade',''))))
                    qualification_on_entry.appendChild(qualgrade)

                #<QUALSBJ>
                if student_data.get('qualsbj',None) is not None:
                    qualsbj = root.createElement('QUALSBJ')
                    qualsbj.appendChild(root.createTextNode(str(student_data.get('qualsbj',''))))
                    qualification_on_entry.appendChild(qualsbj)

                #<QUALSIT>
                if student_data.get('qualsit',None) is not None:
                    qualsit = root.createElement('QUALSIT')
                    qualsit.appendChild(root.createTextNode(str(student_data.get('qualsit',''))))
                    qualification_on_entry.appendChild(qualsit)

                #<QUALTYPE>
                if student_data.get('qualtype',None) is not None:
                    qualtype = root.createElement('QUALTYPE')
                    qualtype.appendChild(root.createTextNode(str(student_data.get('qualtype',''))))
                    qualification_on_entry.appendChild(qualtype)

                #<QUALYEAR>
                if student_data.get('qualyear',None) is not None:
                    qualyear = root.createElement('QUALYEAR')
                    qualyear.appendChild(root.createTextNode(str(student_data.get('qualyear',''))))
                    qualification_on_entry.appendChild(qualyear)


        ##TODO Students Instance - Course
        course_enrollment = frappe.db.sql('''SELECT * FROM `tabCourse Enrollment` WHERE student="%s"''' % student_data.get('name'),as_dict=1)
        for enroll in course_enrollment:
            #<Instance>
            student_instance = root.createElement('Instance')
            student.appendChild(student_instance)

            #<NUMHUS>
            numhus = root.createElement('NUMHUS')
            numhus.appendChild(root.createTextNode(str(student_data.get('numhus',''))))
            student_instance.appendChild(numhus)

            #<OWNINST>
            if company_data.get('owninst',None) is not None:
                owninst = root.createElement('OWNINST')
                owninst.appendChild(root.createTextNode(str(company_data.get('owninst',''))))
                student_instance.appendChild(owninst)

            #<COMDATE>
            comdate = root.createElement('COMDATE')
            comdate.appendChild(root.createTextNode(str(enroll.get('enrollment_date',''))))
            student_instance.appendChild(comdate)
            
            #<ENDDATE>##TODO check where enrollment enddate is???
            enddate = root.createElement('ENDDATE')
            enddate.appendChild(root.createTextNode(str(enroll.get('end_date',''))))
            student_instance.appendChild(enddate)

            #<FUNDCODE>
            ##TODO where will FundCode be
            fundcode = root.createElement('FUNDCODE')
            fundcode.appendChild(root.createTextNode(''))
            student_instance.appendChild(fundcode)

            #<FUNDCOMP>
            ##TODO where will FundCode be
            fundcomp = root.createElement('FUNDCOMP')
            fundcomp.appendChild(root.createTextNode(''))
            student_instance.appendChild(fundcomp)

            #<FUNDLEV>
            ##TODO where will fundLev be
            fundlev = root.createElement('FUNDLEV')
            fundlev.appendChild(root.createTextNode(''))
            student_instance.appendChild(fundlev)

            #<GROSSFEE>
            ##TODO where will Gross Fee be
            gross_fee = root.createElement('GROSSFEE')
            gross_fee.appendChild(root.createTextNode(''))
            student_instance.appendChild(gross_fee)

            #<INTENTLEV>
            ##TODO where will Intended level of MPhil/PhD studies be [where Course.COURSEAIM = L99]
            if course['COURSEAIM'] == 'L99':
                intent_lev = root.createElement('INTENTLEV')
                intent_lev.appendChild(root.createTextNode(''))
                student_instance.appendChild(intent_lev)

            #<NETFEE>
            ##TODO where will Net Fee be [Gross Fee - fund]
            net_fee = root.createElement('NETFEE')
            net_fee.appendChild(root.createTextNode(''))
            student_instance.appendChild(net_fee)

            #<RSNEND>
            ##TODO where will Reason for ending instance be [Instance.ENDDATE == not null]
            reason_end = root.createElement('RSNEND')
            reason_end.appendChild(root.createTextNode(''))
            student_instance.appendChild(reason_end)

            #<SPLENGTH>
            ##TODO where will Expected length of study be
            sp_length = root.createElement('SPLENGTH')
            sp_length.appendChild(root.createTextNode(''))
            student_instance.appendChild(sp_length)

            #<UNITLGTH>
            ##TODO where will Units of length be
            unit_length = root.createElement('UNITLGTH')
            unit_length.appendChild(root.createTextNode(''))
            student_instance.appendChild(unit_length)

            #<FinancialSupport>
            financial_support = root.createElement('FinancialSupport')
            student_instance.appendChild(financial_support)

            #<APPSPEND>##TODO
            app_spend = root.createElement('APPSPEND')
            app_spend.appendChild(root.createTextNode(''))
            financial_support.appendChild(app_spend)

            #<FINAMOUNT>##TODO
            finance_ammount = root.createElement('FINAMOUNT')
            finance_ammount.appendChild(root.createTextNode(''))
            financial_support.appendChild(finance_ammount)

            #<FINTYPE>##TODO
            finance_type = root.createElement('FINTYPE')
            finance_type.appendChild(root.createTextNode(''))
            financial_support.appendChild(finance_type)

        #<StudentEquality>
        student_equality = root.createElement('StudentEquality')
        student.appendChild(student_equality)

        #<DISABLE>
        disable = root.createElement('DISABLE')
        disable.appendChild(root.createTextNode(str(student_data.get('disable',''))))
        student_equality.appendChild(disable)

        #<ETHNIC>
        ethnic = root.createElement('ETHNIC')
        ethnic.appendChild(root.createTextNode(str(student_data.get('ethnic',''))))
        student_equality.appendChild(ethnic)

        #<GENDERID> ##TODO check for gender information and genbder to id relation (depends on database design)
        genderid = root.createElement('GENDERID')
        genderid.appendChild(root.createTextNode(str(student_data.get('genderid',''))))
        student_equality.appendChild(genderid)

        #<NATION> ##TODO check for field name
        nation = root.createElement('NATION')
        nation.appendChild(root.createTextNode(str(student_data.get('nation',''))))
        student_equality.appendChild(nation)

        #<RELBLF> ##TODO check for field name and name to id relation in doctype
        relblf = root.createElement('RELBLF')
        relblf.appendChild(root.createTextNode(str(student_data.get('relblf',''))))
        student_equality.appendChild(relblf)

        #<SEXID> ##TODO check for field name to id relation in doctype
        sexid = root.createElement('SEXID')
        sexid.appendChild(root.createTextNode(str(student_data.get('sexid',''))))
        student_equality.appendChild(sexid)

        #<SEXORT> ##TODO check for how field is stored in database
        sexort = root.createElement('SEXORT')
        sexort.appendChild(root.createTextNode(str(student_data.get('sexort',''))))
        student_equality.appendChild(sexort)
    xml_str = root.toprettyxml(indent ="\t")
    file_name = "{0}/hesa_return/{1}-HESA-{2}.xml".format(directory_path,str(session+company_data['recid']),int(datetime.timestamp(today)))
    doc.return_type = session+company_data['recid']
    doc.file_link = file_name
    doc.file_name =  "{0}-HESA-DC-SA-{1}.xml".format(str(session+company_data['recid']),int(datetime.timestamp(today)))
    doc.insert()
    with open(file_name, "w") as f:
        f.write(xml_str)
    return xml_str