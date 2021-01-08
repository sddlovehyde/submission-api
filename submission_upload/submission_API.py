#!/usr/bin/python3.7
import datetime
import json
import os
import shutil
#import sys
import zipfile
from glob import glob

import http.client
from oauth2client import tools
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

BASE_URL = 'androidpartner.googleapis.com'
DEPLOYMENTS_PATH = '/v1/compatibility/{name=devices/*/products/*/builds/*}'
STORAGE_FILE = 'androidPartner.dat'
SCOPES = 'https://www.googleapis.com/auth/androidPartner'
APPLICATION_NAME = 'androidpartner-cmdline-sample/1.7'
cwd = os.getcwd()
UPLOAD_TYPE_LIST = ("CTS", "GTS", "CTS_Verify", "CTSonAOSP", "VTS", "STS", "CTSApp")


def loadJsonFile(path2File):
    with open(path2File, 'r') as data:
        jsonData = json.load(data)
    return jsonData


def findElement(dictionary, key1, key2, element):
    for i in dictionary:
        if i[key1] == element:
            return i[key2]


def unzip(path2File):
    # a list to save zip file name
    print(path2File)
    zipName = [None] * len(os.listdir(path2File))
    i = 0
    j = 0
    # print os.listdir(path2File)
    # print zipName
    # unzip all zip file in folder(path2File) and save .zip file name to list "zipName"
    for item in os.listdir(path2File):
        if item.find("zip") != -1:
            zipName[i] = item
            # print i
            # print zipName[i]
            with zipfile.ZipFile(path2File + '/' + str(zipName[i]), 'r') as zip_ref:
                zip_ref.extractall(path2File)
            i = i + 1
        else:
            i = i + 1
            # print i
    # print zipName
    # remove none element from list
    print("unzip file number:", i)
    zipName = list(filter(None, zipName))
    for element in zipName:
        print(element)
        zipName[j] = element.rstrip(".zip")
        j = j + 1
    print(zipName)
    return zipName


def uploadReport_1(header):
    conn = http.client.HTTPSConnection(BASE_URL)
    path = '/v1/compatibility/report:startUploadReport'
    headers = header
    conn.request('POST', path, '', headers)
    response = json.loads(conn.getresponse().read())
    print(response)
    ref_name = response["ref"]["name"]
    conn.close()
    return ref_name


def uploadReport_2(header, ref_name, path2report):
    conn = http.client.HTTPSConnection(BASE_URL)
    path = '/upload/v1/media/' + ref_name + '?upload_type=media'
    headers = header
    a = open(path2report, mode='rb')
    print(path)
    print(path2report)
    print("----------upload2-------------")
    conn.request('POST', path, a, headers)
    DumpResponseAndCloseConection(conn)
    print("----------upload2 done-------------")


def uploadReport_3(header, ref_name, companyID):
    conn = http.client.HTTPSConnection(BASE_URL)
    path = '/v1/compatibility/report'
    ref_name = str(ref_name)
    companyID = str(companyID)
    headers = header
    body = {"report_ref": {
        "name": ref_name},
        "company_id": companyID
    }
    body = str(body)
    print(body)
    print("----------upload3-------------")
    conn.request('POST', path, body, headers)
    DumpResponseAndCloseConection(conn)
    print("----------upload3 done-------------")


def GetBuildsList(header):
    conn = http.client.HTTPSConnection(BASE_URL)
    path = DEPLOYMENTS_PATH
    headers = header
    conn.request('GET', path, '', headers)
    DumpResponseAndCloseConection(conn)


def GetResponseAndCloseConection(conn):
    resp = conn.getresponse().read()
    conn.close()


def DumpResponseAndCloseConection(conn):
    resp = conn.getresponse().read().decode('UTF-8')
    print('the response is:\n' + resp)
    conn.close()

    return resp


def CheckCredentials(client_id, client_secret):
    # Checks the OAuth credentials before making a request.
    storage = Storage(STORAGE_FILE)
    credentials = storage.get()
    if (not credentials or credentials.invalid or
            credentials.token_expiry < datetime.datetime.utcnow()):
        flow = OAuth2WebServerFlow(
            client_id=client_id,
            client_secret=client_secret,
            scope=SCOPES,
            user_agent=APPLICATION_NAME)
        credentials = tools.run_flow(flow, storage)
    return {'Authorization': 'Bearer ' + credentials.access_token}


def unzip_and_get_info():
    global submissionPack
    global upload_companyID
    submissionPackName = unzip(cwd)
    print("---------------------")
    print(submissionPackName)
    submissionPack = glob(cwd + "/*/")
    print(submissionPack)

    if submissionPackName:
        print("-----zip mode----")
        print(submissionPack[0])
        CTS_report = unzip(submissionPack[0] + 'Pega_Report/CTS')
        GTS_report = unzip(submissionPack[0] + 'Pega_Report/GTS')
        print(CTS_report)
        if os.path.isfile(submissionPack[0] + 'Pega_Report/CTS/' + CTS_report[
            0] + '/device-info-files/PropertyDeviceInfo.deviceinfo.json') == True:
            CTS_report_property = loadJsonFile(submissionPack[0] + 'Pega_Report/CTS/' + CTS_report[
                0] + '/device-info-files/PropertyDeviceInfo.deviceinfo.json')
            APA_companyID_dict = loadJsonFile(cwd + '/cusomterID.json')
            report_clientID = findElement(CTS_report_property["ro_property"], "name", "value",
                                          "ro.com.google.clientidbase")
            report_fingerprint = findElement(CTS_report_property["ro_property"], "name", "value",
                                             "ro.build.fingerprint")
            upload_companyID = findElement(APA_companyID_dict["customer"], "name", "value", report_clientID)

        elif (os.path.isfile(submissionPack[0] + 'Pega_Report/GTS/' + GTS_report[
            0] + '/device-info-files/PropertyDeviceInfo.deviceinfo.json') == True):
            print("CTS no device info, use GTS report to compare")
            GTS_report_property = loadJsonFile(submissionPack[0] + 'Pega_Report/GTS/' + GTS_report[
                0] + '/device-info-files/PropertyDeviceInfo.deviceinfo.json')
            APA_companyID_dict = loadJsonFile(cwd + '/cusomterID.json')
            report_clientID = findElement(GTS_report_property["ro_property"], "name", "value",
                                          "ro.com.google.clientidbase")
            report_fingerprint = findElement(GTS_report_property["ro_property"], "name", "value",
                                             "ro.build.fingerprint")
            upload_companyID = findElement(APA_companyID_dict["customer"], "name", "value", report_clientID)

        else:
            print("no deviceinfo.json file")

        for item in CTS_report:
            shutil.rmtree(submissionPack[0] + 'Pega_Report/CTS/' + item)

        for item in GTS_report:
            shutil.rmtree(submissionPack[0] + 'Pega_Report/GTS/' + item)

        print("upload company ID:", upload_companyID)
        return report_fingerprint, report_clientID

    elif glob(cwd + "/*/"):
        print("-----folder mode----")
        CTS_report = unzip(submissionPack[0] + 'Pega_Report/CTS')
        GTS_report = unzip(submissionPack[0] + 'Pega_Report/GTS')

        if (os.path.isfile(submissionPack[0] + 'Pega_Report/CTS/' + CTS_report[
            0] + '/device-info-files/PropertyDeviceInfo.deviceinfo.json') == True):
            CTS_report_property = loadJsonFile(submissionPack[0] + 'Pega_Report/CTS/' + CTS_report[
                0] + '/device-info-files/PropertyDeviceInfo.deviceinfo.json')
            APA_companyID_dict = loadJsonFile(cwd + '/cusomterID.json')
            report_clientID = findElement(CTS_report_property["ro_property"], "name", "value",
                                          "ro.com.google.clientidbase")
            report_fingerprint = findElement(CTS_report_property["ro_property"], "name", "value",
                                             "ro.build.fingerprint")
            upload_companyID = findElement(APA_companyID_dict["customer"], "name", "value", report_clientID)

        elif (os.path.isfile(submissionPack[0] + 'Pega_Report/GTS/' + GTS_report[
            0] + '/device-info-files/PropertyDeviceInfo.deviceinfo.json') == True):
            print("CTS no device info, use GTS report to compare")
            GTS_report_property = loadJsonFile(submissionPack[0] + 'Pega_Report/GTS/' + GTS_report[
                0] + '/device-info-files/PropertyDeviceInfo.deviceinfo.json')
            APA_companyID_dict = loadJsonFile(cwd + '/cusomterID.json')
            report_clientID = findElement(GTS_report_property["ro_property"], "name", "value",
                                          "ro.com.google.clientidbase")
            report_fingerprint = findElement(GTS_report_property["ro_property"], "name", "value",
                                             "ro.build.fingerprint")
            upload_companyID = findElement(APA_companyID_dict["customer"], "name", "value", report_clientID)

        else:
            print("no deviceinfo.json file")

        for item in CTS_report:
            shutil.rmtree(submissionPack[0] + 'Pega_Report/CTS/' + item)

        for item in GTS_report:
            shutil.rmtree(submissionPack[0] + 'Pega_Report/GTS/' + item)

        print("upload company ID:", upload_companyID)
        return report_fingerprint, report_clientID

    else:
        print("empty")
        report_fingerprint = "null"
        report_clientID = "null"

        return report_fingerprint, report_clientID


def upload():
    header = CheckCredentials('973714329395-r1cjtidkf8jgutb4f2gno2dg9671av81.apps.googleusercontent.com',
                              '_hKnrk2l6ilGgnie9D4n_lJt')
    ref_name = uploadReport_1(header)
    for item in UPLOAD_TYPE_LIST:
        i = 0
        report_name = os.listdir(submissionPack[0] + 'Pega_Report/' + item)
        print("report name")
        print(report_name)
        for sub_item in report_name:
            report_location = submissionPack[0] + 'Pega_Report/' + item + '/' + sub_item
            print(report_location)
            print('******')
            uploadReport_2(header, ref_name, report_location)
            uploadReport_3(header, ref_name, upload_companyID)
            i = i + 1

'''
def main(argv):
    # Developer must pass the project client ID and API key.
    header = CheckCredentials('973714329395-r1cjtidkf8jgutb4f2gno2dg9671av81.apps.googleusercontent.com',
                              '_hKnrk2l6ilGgnie9D4n_lJt')

    # upzip submission pack & CTS report and get package & CTS folder name
    print("----testing----")
    submissionPack = unzip(cwd)
    CTS_report = unzip(cwd + '/' + submissionPack[0] + '/Pega_Report/CTS')

    # load json info and check CTS report client id in customerID.json
    # get report client ID and upload companyID
    CTS_report_property = loadJsonFile(cwd + '/' + submissionPack[0] + '/Pega_Report/CTS/' + CTS_report[
        0] + '/device-info-files/PropertyDeviceInfo.deviceinfo.json')
    APA_companyID_dict = loadJsonFile(cwd + '/cusomterID.json')
    report_clientID = findElement(CTS_report_property["ro_property"], "name", "value", "ro.com.google.clientidbase")
    upload_companyID = findElement(APA_companyID_dict["customer"], "name", "value", report_clientID)
    print(upload_companyID)

    # remove CTS folder
    for item in CTS_report:
        shutil.rmtree(cwd + '/' + submissionPack[0] + '/Pega_Report/CTS/' + item)
    ref_name = uploadReport_1(header)

    # upload report
    for item in UPLOAD_TYPE_LIST:
        i = 0
        report_name = os.listdir(cwd + '/' + submissionPack[0] + '/Pega_Report/' + item)
        for sub_item in report_name:
            report_location = cwd + '/' + submissionPack[0] + '/Pega_Report/' + item + '/' + sub_item
            print(report_location)
            print('******')
            # uploadReport_2(header, ref_name, report_location)
            # uploadReport_3(header, ref_name, upload_companyID)
            i = i + 1


if __name__ == '__main__':
    main(sys.argv)
'''