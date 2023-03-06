def DriftInfo_from_xes_all(path):

    drifts = list()
    os.chdir(path)
    for file in glob.glob("*.xes"):
        if __name__ == "__main__":
            log = pm4py.read_xes(path+"/"+str(file))
            l = list(log.attributes[list(log.attributes.keys())[0]]["children"].values())
            print(l)
        DI = DriftInfo(*l)
        drifts.append(DI)

    return drifts


def DriftInfo_from_xes_single(path): #Here the path should lead to a specific file
    if __name__ == "__main__":
        log = pm4py.read_xes(path)
        l = list(log.attributes[list(log.attributes.keys())[0]]["children"].values())
        print(l)
    DI = DriftInfo(*l)

    return DI

x = DriftInfo_from_xes_single("C:/Users/ziedk/OneDrive/Bureau/New folder/cdlg_tool_dev/data/generated_collections/1677854543/log_0.xes")
print(x)