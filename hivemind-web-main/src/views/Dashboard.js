import React from 'react';
import clsx from 'clsx';
import {makeStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Container from '@material-ui/core/Container';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import Chart from '../components/Chart';
import AccountValue from '../components/AccountValue';
import OpenTrades from '../components/OpenTrades';
import RedditList from "../components/RedditList"
import Portfolio from "../components/Portfolio";
import AccountCash from "../components/AccountCash";

const drawerWidth = 600;

const useStyles = makeStyles((theme) => ({
    root: {
        display: 'flex',
    },
    appBar: {
        zIndex: theme.zIndex.drawer + 1,
    },
    drawer: {
        width: drawerWidth,
        flexShrink: 0,
    },
    drawerPaper: {
        width: drawerWidth,
    },
    drawerContainer: {
        overflow: 'auto',
    },
    content: {
        flexGrow: 1,
        padding: theme.spacing(3),
    },
    fixedHeight: {
        height: 280,
    },
    paper: {
        padding: theme.spacing(2),
        display: 'flex',
        overflow: 'auto',
        flexDirection: 'column',
    },
}));

export default function Dashboard() {
    const classes = useStyles();
    const fixedHeightPaper = clsx(classes.paper, classes.fixedHeight);

    return (
        <div className={classes.root}>
            <CssBaseline/>
            <AppBar position="fixed" className={classes.appBar}>
                <Toolbar>
                    <Typography variant="h6" noWrap>
                        Hivemind
                    </Typography>
                </Toolbar>
            </AppBar>
            <Drawer
                className={classes.drawer}
                variant="permanent"
                classes={{
                    paper: classes.drawerPaper,
                }}
            >
                <Toolbar/>
                <div className={classes.drawerContainer}>
                    <RedditList/>
                </div>
            </Drawer>
            <main className={classes.content}>
                <Toolbar/>
                <Container maxWidth={false} className={classes.container}>
                    <Grid container spacing={3}>
                        {/* Chart */}
                        <Grid item xs={12} lg={8}>
                            <Paper className={fixedHeightPaper}>
                                <Chart/>
                            </Paper>
                        </Grid>
                        {/* Account value */}
                        <Grid item xs={12} lg={2}>
                            <Paper className={fixedHeightPaper}>
                                <AccountValue/>
                            </Paper>
                        </Grid>
                        {/* Account cash */}
                        <Grid item xs={12} lg={2}>
                            <Paper className={fixedHeightPaper}>
                                <AccountCash/>
                            </Paper>
                        </Grid>
                        {/* Portfolio */}
                        <Grid item xs={12}>
                            <Paper className={classes.paper}>
                                <Portfolio/>
                            </Paper>
                        </Grid>
                        {/* Open trades */}
                        <Grid item xs={12}>
                            <Paper className={classes.paper}>
                                <OpenTrades/>
                            </Paper>
                        </Grid>
                    </Grid>
                </Container>
            </main>
        </div>
    );
}