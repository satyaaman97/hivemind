import React, {useEffect, useState} from 'react';
import {useTheme} from '@material-ui/core/styles';
import {Label, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis} from 'recharts';
import Typography from '@material-ui/core/Typography';

export default function Chart() {
    const [chartData, setChartData] = useState({});

    const transformChartData = (data) => {
        const transformedData = data["xAxis"][0]["data"].map((value, index) => {
            return {
                "date": value,
                "portfolio": data["series"][0]["data"][index],
                "sp": data["series"][1]["data"][index],
            }
        }).filter(d => d["portfolio"] !== undefined && d["sp"] !== undefined);

        setChartData(transformedData);
    };

    useEffect(() => {
        fetch("https://us-central1-tenacious-camp-304921.cloudfunctions.net/portfolio_chart", {}).then(res => res.json()).then(res => {
            transformChartData(res);
        });
    }, []);

    const theme = useTheme();

    return (
        <React.Fragment>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
                Historical Account Value
            </Typography>
            <ResponsiveContainer>
                <LineChart
                    data={chartData}
                    margin={{
                        top: 16,
                        right: 16,
                        bottom: 0,
                        left: 24,
                    }}
                >
                    <XAxis dataKey="date" stroke={theme.palette.text.secondary}/>
                    <YAxis stroke={theme.palette.text.secondary}>
                        <Label
                            angle={270}
                            position="left"
                            style={{textAnchor: 'middle', fill: theme.palette.text.primary}}
                        >
                            Change (%)
                        </Label>
                    </YAxis>
                    <Tooltip formatter={value => value + " %"}/>
                    <Legend/>
                    <Line name="Portfolio" type="monotone" dataKey="portfolio" stroke={theme.palette.primary.main}/>
                    <Line name="S&P 500" type="monotone" dataKey="sp" stroke={theme.palette.secondary.main}/>
                </LineChart>
            </ResponsiveContainer>
        </React.Fragment>
    );
}