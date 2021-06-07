import React, {useEffect, useState} from 'react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Typography from '@material-ui/core/Typography';
import TableContainer from '@material-ui/core/TableContainer';

export default function OpenTrades() {

    const [openTrades, setOpenTrades] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("https://us-central1-tenacious-camp-304921.cloudfunctions.net/open_trades", {}).then(res => res.json()).then(res => {
            setOpenTrades(res);
            setLoading(false);
        });
    }, []);

    return (
        <React.Fragment>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
                Open Trades
            </Typography>

            <TableContainer>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Order ID</TableCell>
                            <TableCell>Symbol</TableCell>
                            <TableCell>Trade Type</TableCell>
                            <TableCell>Quantity</TableCell>
                            <TableCell>Order Date</TableCell>
                            <TableCell align="right">Order Price</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {!loading &&
                        openTrades.map((trade) => (
                            <TableRow key={trade.order_id}>
                                <TableCell>{trade.order_id}</TableCell>
                                <TableCell>{trade.symbol}</TableCell>
                                <TableCell>{trade.trade_type}</TableCell>
                                <TableCell>{trade.quantity}</TableCell>
                                <TableCell>{trade.order_date}</TableCell>
                                <TableCell align="right">${trade.order_price}</TableCell>
                            </TableRow>
                        ))
                        }
                    </TableBody>
                </Table>
            </TableContainer>
        </React.Fragment>
    );
}