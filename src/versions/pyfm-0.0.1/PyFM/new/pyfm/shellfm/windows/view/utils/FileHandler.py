
import os, shutil, subprocess, threading


class FileHandler:
    def create_file(self, nFile):
        pass

    def update_file(self, oFile, nFile):
        try:
            print(f"Renaming:  {oFile}  -->  {nFile}")
            os.rename(oFile, nFile)
            return True
        except Exception as e:
            print("An error occured renaming the file:")
            print(e)
            return False

    def delete_file(self, toDeleteFile):
        try:
            print(f"Deleting:  {toDeleteFile}")
            if os.path.exists(toDeleteFile):
                if os.path.isfile(toDeleteFile):
                    os.remove(toDeleteFile)
                elif os.path.isdir(toDeleteFile):
                    shutil.rmtree(toDeleteFile)
                else:
                    print("An error occured deleting the file:")
                    return False
            else:
                print("The folder/file does not exist")
                return False
        except Exception as e:
            print("An error occured deleting the file:")
            print(e)
            return False

        return True

    def move_file(self, fFile, tFile):
        try:
            print(f"Moving:  {fFile}  -->  {tFile}")
            if os.path.exists(fFile) and os.path.exists(tFile):
                if not tFile.endswith("/"):
                    tFile += "/"

                shutil.move(fFile, tFile)
            else:
                print("The folder/file does not exist")
                return False
        except Exception as e:
            print("An error occured moving the file:")
            print(e)
            return False

        return True

    def copy_file(self):
        pass

    def cut_file(self):
        pass

    def paste_file(self):
        pass
