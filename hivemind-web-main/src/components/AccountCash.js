import React, {useEffect, useState} from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles({
    balanceContext: {
        flex: 1,
    },
});

export default function AccountCash() {

    const [accountCash, setAccountCash] = useState("N/A");
    const [loading, setLoading] = useState(true);
    const currentTime = useState(Date().toLocaleString())[0];

    useEffect(() => {
        fetch("https://us-central1-tenacious-camp-304921.cloudfunctions.net/get_cash", {}).then(res => res.json()).then(res => {
            setAccountCash(res["account_cash"]);
            setLoading(false);
        });
    }, []);

    const classes = useStyles();
    return (
        <React.Fragment>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
                Account Cash
            </Typography>
            <Typography component="p" variant="h4">
                {loading ? "Loading..." : "$" + accountCash}
            </Typography>
            <Typography color="textSecondary" className={classes.balanceContext}>
                as of {currentTime}
            </Typography>
        </React.Fragment>
    );
}