import prettytable
import re
from PyQt5.QtWidgets import QApplication

def content():
    strlist = []
    helpstr = ''  #@UnusedVariable
    newline = '\n'  #@UnusedVariable
    strlist.append('<head><style> td, th {border: 1px solid #ddd;  padding: 6px;} th {padding-top: 6px;padding-bottom: 6px;text-align: left;background-color: #0C6AA6; color: white;} </style></head> <body>')
    strlist.append("<b>")
    strlist.append(QApplication.translate('HelpDlg','Energy and CO2 Calculator',None))
    strlist.append("</b>")
    tbl_Introtop = prettytable.PrettyTable()
    tbl_Introtop.header = False
    tbl_Introtop.add_row([QApplication.translate('HelpDlg','The Energy tab shows a roast&#39;s energy consumption.   CO2 emissions are also calculated to monitor the impact of the roasting operation.  Settings must be made for the main burners and afterburner.  The energy used for preheating and between batch protocols are included in the calculations, and settings are available for them as well.   Follow the steps below to set the energy inputs for the roast machine and afterburner.',None)])
    strlist.append(tbl_Introtop.get_html_string(attributes={"width":"100%","border":"1","padding":"1","border-collapse":"collapse"}))
    strlist.append("<br/><br/><b>")
    strlist.append(QApplication.translate('HelpDlg','1. Burners Tab',None))
    strlist.append("</b>")
    tbl_Burnerstop = prettytable.PrettyTable()
    tbl_Burnerstop.header = False
    tbl_Burnerstop.add_row([QApplication.translate('HelpDlg','Begin by making entries on the Burners tab.  ',None)+newline+QApplication.translate('HelpDlg','Power ratings for upto four burners may be entered.  Many roasting machines will use only one burner entry for the main burner.  An afterburner should be entered as a separate burner.  ',None)+newline+QApplication.translate('HelpDlg','Burner entries require knowing the power rating of the burner.  Roasting machine manufacturer&#39;s typically provide this information.  If this information is not available for a specific machine an estimate based on the machine capacity is available on the artisan-scope.org website.',None)])
    strlist.append(tbl_Burnerstop.get_html_string(attributes={"width":"100%","border":"1","padding":"1","border-collapse":"collapse"}))
    tbl_Burners = prettytable.PrettyTable()
    tbl_Burners.field_names = [QApplication.translate('HelpDlg','Field',None),QApplication.translate('HelpDlg','Description',None)]
    tbl_Burners.add_row([QApplication.translate('HelpDlg','Label',None),QApplication.translate('HelpDlg','Enter your personal description for this burner.  Examples are &#39;Main&#39; and &#39;Afterburner&#39;.',None)])
    tbl_Burners.add_row([QApplication.translate('HelpDlg','Rating',None),QApplication.translate('HelpDlg','This is the power rating of the burner.  Choose the units in the next column.  ',None)])
    tbl_Burners.add_row([QApplication.translate('HelpDlg','Unit',None),QApplication.translate('HelpDlg','Select the appropriate power unit. Some manufactuers incorrectly use BTU/hr.  In that case use BTU for th eunit.',None)])
    tbl_Burners.add_row([QApplication.translate('HelpDlg','Fuel',None),QApplication.translate('HelpDlg','Select the type of fuel used by your roaster.  &#39;Elec&#39; is assumed to be electricity generated from dirty sources such as coal.  If you roaster is heated by clean electricity choose the blank entry.',None)])
    tbl_Burners.add_row([QApplication.translate('HelpDlg','Event',None),QApplication.translate('HelpDlg','When blank the burner is assumed to be at a constant setting, which is the &#39;Value 100%&#39; multiplied by the rating.  Special Events are often used to record the burner setting in the roast profile.  Select the Event that corresponds to the urner setting here.',None)])
    tbl_Burners.add_row([QApplication.translate('HelpDlg','Value 0%',None),QApplication.translate('HelpDlg','When an Event is selected in the previous column this value can be set to match the 0% burner setting to the event setting.  In most cases a 0 Event value will correspond to the 0% burner setting.',None)])
    tbl_Burners.add_row([QApplication.translate('HelpDlg','Value 100%',None),QApplication.translate('HelpDlg','When an Event is selected this value can be set to match the 100% burner setting to the event setting.  This is useful when the 100% burner setting is recorded as a different number in the Event.  For instance, maybe the burner event is recorded as 10x the kPa reading on the gas manometer.  An event value of 30 is recoded to signify 3 kPa.  If the 100% burner setting corresponds to 6 kPa then the &#39;Value 100%&#39; should be set to 60.  (10x 6 = 60).',None)])
    strlist.append(tbl_Burners.get_html_string(attributes={"width":"100%","border":"1","padding":"1","border-collapse":"collapse"}))
    tbl_Burnersbottom = prettytable.PrettyTable()
    tbl_Burnersbottom.header = False
    tbl_Burnersbottom.add_row([QApplication.translate('HelpDlg','NOTE:  The Bernoulli settings from Config> Events> Sliders are used to apply Bernoulli&#39;s law for non-linear gas flows. ',None)])
    strlist.append(tbl_Burnersbottom.get_html_string(attributes={"width":"100%","border":"1","padding":"1","border-collapse":"collapse"}))
    strlist.append("<br/><br/><b>")
    strlist.append(QApplication.translate('HelpDlg','2. Protocol Tab',None))
    strlist.append("</b>")
    tbl_Protocoltop = prettytable.PrettyTable()
    tbl_Protocoltop.header = False
    tbl_Protocoltop.add_row([QApplication.translate('HelpDlg','The Protocol settings allow including Preheating and Between Batch Protocol (BBP) energy consumption.  There are two ways to specify these values.  The first assumes a constant burner setting for a defined period of time.  An example for Preheating is to set a Duration of 45:00 (45 minutes) at 30% Burner setting.  Percentages may be entered either as a decimal (.30) or a percentage (30%).  When a percentage is entered there a corresponding Duration must be entered.',None)+newline+QApplication.translate('HelpDlg','',None)+newline+QApplication.translate('HelpDlg','The second type of entry is a measured energy value.  This is any value greater than 1.0.  The value can be found by direct measurement using Artisan.  Here are instructions for how to make this measurement.',None)+newline+QApplication.translate('HelpDlg','',None)+newline+QApplication.translate('HelpDlg','An Event must be used to record the burner settings.  Make sure all the values on the Protocol tab are blank or zero.  START a profile recording in Artisan at the beginning of the protocol.  For preheating that would be when the burner(s) are first turned on.  For BBP is will be the start of BBP, usually at the end of the previous roast or the end of preheating.  Record any burner setting changes in the appropriate event.  STOP the recording at the end of the protocol.  Save the recorded protocol for safe keeping.  Review the energy used results.  The units that results are displayed in may need to be changed to match the units set on the Burners tab.  If there are multiple burners used it may be necessary to add up the energy used for each individual burner from the table in the Details tab.  Note that clicking &#39;Copy Table&#39; copies the table in CSV format to the clipboard.  Pasting into a spread sheet makes it easy to manipulate the data.',None)])
    strlist.append(tbl_Protocoltop.get_html_string(attributes={"width":"100%","border":"1","padding":"1","border-collapse":"collapse"}))
    tbl_Protocol = prettytable.PrettyTable()
    tbl_Protocol.field_names = [QApplication.translate('HelpDlg','Field',None),QApplication.translate('HelpDlg','Description',None)]
    tbl_Protocol.add_row([QApplication.translate('HelpDlg','Preheating',None),QApplication.translate('HelpDlg','This row sets the values for preheating for the roasting session.  Percentag or measured values may be netered for each burner.  When a percentage is used the Duration field must be set.',None)])
    tbl_Protocol.add_row([QApplication.translate('HelpDlg','Between Batches',None),QApplication.translate('HelpDlg','This row sets the values for between batch protocol for the roasting session.  Percentag or measured values may be netered for each burner.  When a percentage is used the Duration field must be set.',None)])
    tbl_Protocol.add_row([QApplication.translate('HelpDlg','Duration',None),QApplication.translate('HelpDlg','The length (mm:ss) of protocol.  It is used with a burner&#39;s percentage setting to calculate the energy consumed  by that burner.  When a percentage entry is made for the burner, the Duration field must be set.',None)])
    tbl_Protocol.add_row([QApplication.translate('HelpDlg','Measured Energy or Output %',None),QApplication.translate('HelpDlg','The value is either the measured energy for the protocol or the burner constant percentage setting for the length of the Duration field.',None)])
    tbl_Protocol.add_row([QApplication.translate('HelpDlg','Between Batches after Pre-Heating',None),QApplication.translate('HelpDlg','If a Between Batches protocol run is done after the Preheating and before the roast, this flag should be ticked',None)])
    strlist.append(tbl_Protocol.get_html_string(attributes={"width":"100%","border":"1","padding":"1","border-collapse":"collapse"}))
    tbl_Protocolbottom = prettytable.PrettyTable()
    tbl_Protocolbottom.header = False
    tbl_Protocolbottom.add_row([QApplication.translate('HelpDlg','NOTE:  The Bernoulli settings from Config> Events> Sliders are used to apply Bernoulli&#39;s law for non-linear gas flows. ',None)+newline+QApplication.translate('HelpDlg','http://artisan-scope.org',None)])
    strlist.append(tbl_Protocolbottom.get_html_string(attributes={"width":"100%","border":"1","padding":"1","border-collapse":"collapse"}))
    strlist.append("<br/><br/><b>")
    strlist.append(QApplication.translate('HelpDlg','Details',None))
    strlist.append("</b>")
    strlist.append("</body>")
    helpstr = "".join(strlist)
    helpstr = re.sub(r"&amp;", r"&",helpstr)
    return helpstr