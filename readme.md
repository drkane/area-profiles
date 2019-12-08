## Copy files to server

```
scp -r ./data/ root@ip-address:s/var/lib/dokku/data/storage/areaprofiles
```

## dokku configuration

need to set

```
dokku config:set areaprofiles DATA_DIR='/app/data/data'
```