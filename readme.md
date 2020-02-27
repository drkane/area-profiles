## Copy files to server

```
scp -r ./data/ root@ip-address:/var/lib/dokku/data/storage/areaprofiles
```

## dokku configuration

need to set

```
mkdir -p  /var/lib/dokku/data/storage/areas
chown -R dokku:dokku /var/lib/dokku/data/storage/areas
chown -R 32767:32767 /var/lib/dokku/data/storage/areas
dokku storage:mount areas /var/lib/dokku/data/storage/areas:/app/storage
dokku config:set areas DATA_DIR='/app/storage'
```