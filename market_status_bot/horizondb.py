from peewee import *
import configparser

config = configparser.ConfigParser()
config.read('bot.cfg')
h_cfg = config['horizon-db']





database = PostgresqlDatabase(h_cfg['dbname'], host=h_cfg['host'], user=h_cfg['user'], password=h_cfg['password'])

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class GorpMigrations(BaseModel):
    applied_at = DateTimeField(null=True)
    id = TextField(primary_key=True)

    class Meta:
        db_table = 'gorp_migrations'

class HistoryAccounts(BaseModel):
    address = CharField(null=True, unique=True)
    id = BigIntegerField(unique=True)

    class Meta:
        db_table = 'history_accounts'

class HistoryEffects(BaseModel):
    details = JSONField(null=True)
    history_account = BigIntegerField(db_column='history_account_id')
    history_operation = BigIntegerField(db_column='history_operation_id')
    order = IntegerField()
    type = IntegerField(index=True)

    class Meta:
        db_table = 'history_effects'
        indexes = (
            (('history_account', 'history_operation', 'order'), True),
            (('history_operation', 'order'), True),
        )

class HistoryLedgers(BaseModel):
    base_fee = IntegerField()
    base_reserve = IntegerField()
    closed_at = DateTimeField(index=True)
    created_at = DateTimeField(null=True)
    fee_pool = BigIntegerField()
    id = BigIntegerField(null=True, unique=True)
    importer_version = IntegerField(index=True)
    ledger_hash = CharField(unique=True)
    max_tx_set_size = IntegerField()
    operation_count = IntegerField()
    previous_ledger_hash = CharField(null=True, unique=True)
    sequence = IntegerField(unique=True)
    total_coins = BigIntegerField()
    transaction_count = IntegerField()
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'history_ledgers'

class HistoryOperationParticipants(BaseModel):
    history_account = BigIntegerField(db_column='history_account_id')
    history_operation = BigIntegerField(db_column='history_operation_id', index=True)

    class Meta:
        db_table = 'history_operation_participants'
        indexes = (
            (('history_operation', 'history_account'), True),
        )

class HistoryOperations(BaseModel):
    application_order = IntegerField()
    details = JSONField(null=True)
    id = BigIntegerField(unique=True)
    source_account = CharField()
    transaction = BigIntegerField(db_column='transaction_id', index=True)
    type = IntegerField(index=True)

    class Meta:
        db_table = 'history_operations'

class HistoryTransactionParticipants(BaseModel):
    history_account = BigIntegerField(db_column='history_account_id')
    history_transaction = BigIntegerField(db_column='history_transaction_id', index=True)

    class Meta:
        db_table = 'history_transaction_participants'
        indexes = (
            (('history_transaction', 'history_account'), True),
        )

class HistoryTransactions(BaseModel):
    account = CharField()
    account_sequence = BigIntegerField()
    application_order = IntegerField()
    created_at = DateTimeField(null=True)
    fee_paid = IntegerField()
    id = BigIntegerField(null=True, unique=True)
    ledger_sequence = IntegerField()
    memo = CharField(null=True)
    memo_type = CharField()
    operation_count = IntegerField()
    signatures = UnknownField()  # ARRAY
    time_bounds = UnknownField(null=True)  # int8range
    transaction_hash = CharField(index=True)
    tx_envelope = TextField()
    tx_fee_meta = TextField()
    tx_meta = TextField()
    tx_result = TextField()
    updated_at = DateTimeField(null=True)

    class Meta:
        db_table = 'history_transactions'
        indexes = (
            (('account', 'account_sequence'), False),
            (('ledger_sequence', 'application_order'), False),
        )

