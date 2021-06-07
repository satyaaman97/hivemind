import React, {useEffect, useState} from 'react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Typography from '@material-ui/core/Typography';
import TableContainer from '@material-ui/core/TableContainer';

export default function Portfolio() {

    const [portfolio, setPortfolio] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("https://us-central1-tenacious-camp-304921.cloudfunctions.net/stock_portfolio", {}).then(res => res.json()).then(res => {
            setPortfolio(res);
            setLoading(false);
        });
    }, []);

    return (
        <React.Fragment>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
                Stock Portfolio
            </Typography>

            <TableContainer>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Symbol</TableCell>
                            <TableCell>Description</TableCell>
                            <TableCell>Quantity</TableCell>
                            <TableCell>Purchase Price</TableCell>
                            <TableCell>Current Price</TableCell>
                            <TableCell align="right">Total Value</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {!loading &&
                        portfolio.map((stock) => (
                            <TableRow key={stock.symbol}>
                                <TableCell>{stock.symbol}</TableCell>
                                <TableCell>{stock.description}</TableCell>
                                <TableCell>{stock.quantity}</TableCell>
                                <TableCell>${stock.purchase_price}</TableCell>
                                <TableCell>${stock.current_price}</TableCell>
                                <TableCell align="right">${stock.total_value}</TableCell>
                            </TableRow>
                        ))
                        }
                    </TableBody>
                </Table>
            </TableContainer>
        </React.Fragment>
    );
}