####################################################################################################
####################################################################################################
###
###     RESET ALL THE DATABASES
###     This script delete and recreate any instance of the databases in architecture/files
###
###     WARNING: this script will delete all the data in the databases
###
###     Usage:
###     Run 'sh ./resetDB.sh' on your prompt to initialize (or re-initialize) the github directory      
###
####################################################################################################                                                                                                  
####################################################################################################

# Go to the directory where the databases are stored
cd files

# Delete and recreate the databases attribute_certifier
cd attribute_certifier
rm -f attribute_certifier.db
sqlite3 attribute_certifier.db < ../commands.sql
echo "attribute_certifier.db resetted (1/5)"

# Delete and recreate the databases data_owner
cd ../data_owner
rm -f data_owner.db
sqlite3 data_owner.db < ../commands.sql
echo "data_owner.db resetted (2/5)"

# Delete and recreate the databases reader
cd ../reader
rm -f reader.db
sqlite3 reader.db < ../commands.sql
echo "reader.db resetted (3/5)"

# Delete and recreate the databases sdm
cd ../sdm
rm -f sdm.db
sqlite3 sdm.db < ../commands.sql
echo "sdm.db resetted (4/5)"

# Delete and recreate the databases skm
cd ../skm
rm -f skm.db
sqlite3 skm.db < ../commands.sql
echo "skm.db resetted (5/5)"