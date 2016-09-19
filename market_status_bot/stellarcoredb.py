from peewee import *
import configparser

config = configparser.ConfigParser()
config.read('bot.cfg')
sc_cfg = config['stellar_core_db']


database = PostgresqlDatabase(sc_cfg['dbname'], host=sc_cfg['host'], user=sc_cfg['user'], password=sc_cfg['password'])


class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class Accountdata(BaseModel):
    accountid = CharField()
    dataname = CharField()
    datavalue = CharField()

    class Meta:
        db_table = 'accountdata'
        indexes = (
            (('accountid', 'dataname'), True),
        )
        primary_key = CompositeKey('accountid', 'dataname')

class Accounts(BaseModel):
    accountid = CharField(primary_key=True)
    balance = BigIntegerField(index=True)
    flags = IntegerField()
    homedomain = CharField()
    inflationdest = CharField(null=True)
    lastmodified = IntegerField()
    numsubentries = IntegerField()
    seqnum = BigIntegerField()
    thresholds = TextField()

    class Meta:
        db_table = 'accounts'

class Ban(BaseModel):
    nodeid = CharField(primary_key=True)

    class Meta:
        db_table = 'ban'

class Ledgerheaders(BaseModel):
    bucketlisthash = CharField()
    closetime = BigIntegerField()
    data = TextField()
    ledgerhash = CharField(primary_key=True)
    ledgerseq = IntegerField(index=True, null=True)
    prevhash = CharField()

    class Meta:
        db_table = 'ledgerheaders'

class Offers(BaseModel):
    amount = BigIntegerField()
    buyingassetcode = CharField(null=True)
    buyingassettype = IntegerField()
    buyingissuer = CharField(index=True, null=True)
    flags = IntegerField()
    lastmodified = IntegerField()
    offerid = BigIntegerField(primary_key=True)
    price = FloatField(index=True)
    priced = IntegerField()
    pricen = IntegerField()
    sellerid = CharField()
    sellingassetcode = CharField(null=True)
    sellingassettype = IntegerField()
    sellingissuer = CharField(index=True, null=True)

    class Meta:
        db_table = 'offers'

class Peers(BaseModel):
    ip = CharField()
    nextattempt = DateTimeField()
    numfailures = IntegerField()
    port = IntegerField()

    class Meta:
        db_table = 'peers'
        indexes = (
            (('ip', 'port'), True),
        )
        primary_key = CompositeKey('ip', 'port')

class Publishqueue(BaseModel):
    ledger = PrimaryKeyField()
    state = TextField(null=True)

    class Meta:
        db_table = 'publishqueue'

class Pubsub(BaseModel):
    lastread = IntegerField(null=True)
    resid = CharField(primary_key=True)

    class Meta:
        db_table = 'pubsub'

class Scphistory(BaseModel):
    envelope = TextField()
    ledgerseq = IntegerField(index=True)
    nodeid = CharField()

    class Meta:
        db_table = 'scphistory'

class Scpquorums(BaseModel):
    lastledgerseq = IntegerField()
    qset = TextField()
    qsethash = CharField(primary_key=True)

    class Meta:
        db_table = 'scpquorums'

class Signers(BaseModel):
    accountid = CharField(index=True)
    publickey = CharField()
    weight = IntegerField()

    class Meta:
        db_table = 'signers'
        indexes = (
            (('accountid', 'publickey'), True),
        )
        primary_key = CompositeKey('accountid', 'publickey')

class Storestate(BaseModel):
    state = TextField(null=True)
    statename = CharField(primary_key=True)

    class Meta:
        db_table = 'storestate'

class Trustlines(BaseModel):
    accountid = CharField()
    assetcode = CharField()
    assettype = IntegerField()
    balance = BigIntegerField()
    flags = IntegerField()
    issuer = CharField()
    lastmodified = IntegerField()
    tlimit = BigIntegerField()

    class Meta:
        db_table = 'trustlines'
        indexes = (
            (('accountid', 'issuer', 'assetcode'), True),
        )
        primary_key = CompositeKey('accountid', 'assetcode', 'issuer')

class Txfeehistory(BaseModel):
    ledgerseq = IntegerField(index=True)
    txchanges = TextField()
    txid = CharField()
    txindex = IntegerField()

    class Meta:
        db_table = 'txfeehistory'
        indexes = (
            (('ledgerseq', 'txindex'), True),
        )
        primary_key = CompositeKey('ledgerseq', 'txindex')

class Txhistory(BaseModel):
    ledgerseq = IntegerField(index=True)
    txbody = TextField()
    txid = CharField()
    txindex = IntegerField()
    txmeta = TextField()
    txresult = TextField()

    class Meta:
        db_table = 'txhistory'
        indexes = (
            (('ledgerseq', 'txindex'), True),
        )
        primary_key = CompositeKey('ledgerseq', 'txindex')

