from rest_framework import serializers
from user_accounts.models import User, Account, Transaction


class AccRelatedSerializer(serializers.RelatedField):
    def to_native(self, acc):
        return {
            'balance': acc.balance,
            'created_at': acc.created_at,
            'updated_at': acc.modified_at
        }


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['title', 'trans_type', 'amount',
                  'is_pending', 'created_at', 'modified_at', 'confirmed_at']
        extra_kwargs = {
            'title': {'read_only': True},
            'trans_type': {'read_only': True},
            'amount': {'read_only': True},
            'is_pending': {'read_only': True},
            'confirmed_at': {'read_only': True},
            'created_at': {'read_only': True},
        }


class AccountSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True)

    class Meta:
        model = Account
        fields = ['id', 'balance', 'created_at',
                  'is_active', 'modified_at', 'transactions']
        read_only_fields = ['balance', 'is_active', 'id',
                            'transactions', 'created_at', 'modified_at']
        extra_kwargs = {
            'balance': {'read_only': True},
            'is_active': {'read_only': True},
            'id': {'read_only': True},
            'transactions': {'read_only': True},
            'created_at': {'read_only': True},
            'modified_at': {'read_only': True},
        }


class UserSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(
    #     view_name='user-detail',
    #     lookup_field='phonenumber'
    # )
    wallet = AccountSerializer(many=False, required=False)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def create(self, validated_data):
        fields = ['phonenumber', 'password', 'username', 'middle_name',
                  'address', 'first_name', 'last_name', 'email', 'avatar']
        data = {f: validated_data.get(f) for f in fields}
        print(data)
        return User.objects.create_user(**data)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phonenumber', 'username', 'password',
            'first_name', 'middle_name', 'last_name', 'is_producer', 'is_secretary',
            'address', 'wallet', 'avatar']
        read_only_fields = ['wallet', 'is_producer', 'is_secretary']
        depth = 1
        extra_kwargs = {
            'wallet': {'read_only': True},
            'is_producer': {'read_only': True},
            'is_secretary': {'read_only': True},
        }


class AllUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phonenumber', 'username', 'email']
        read_only_fields = ['phonenumber', 'username']
