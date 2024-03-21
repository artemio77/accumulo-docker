#!/bin/bash

docker exec -i accumulo-accumulo-master-1 /bin/bash <<EOF
accumulo shell -u root <<INNER_EOF
createuser accumulo
accumulo
accumulo
createtable stock_data
grant Table.READ -t stock_data -u accumulo
grant Table.WRITE -t stock_data -u accumulo
grant Table.BULK_IMPORT -t stock_data -u accumulo
INNER_EOF
EOF
