import React, {useEffect, useState} from "react";
import Divider from "@material-ui/core/Divider";
import List from "@material-ui/core/List";
import {ListItem, ListItemIcon, ListItemText, Typography} from "@material-ui/core";
import RedditIcon from '@material-ui/icons/Reddit';
import makeStyles from "@material-ui/core/styles/makeStyles";


const useStyles = makeStyles(() => ({
    boldText: {
        fontWeight: "bold"
    }
}));


export default function RedditList() {

    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("https://www.reddit.com/r/wallstreetbets.json").then(res => res.json()).then(function (res) {
            setPosts(res.data.children);
            setLoading(false);
        });
    }, []);

    const truncate = (input) => input.length > 500 ? `${input.substring(0, 250)}...` : input;

    const classes = useStyles();

    return (
        <div>
            <List>
                <ListItem>
                    <ListItemIcon><RedditIcon/></ListItemIcon>
                    <ListItemText primary={
                        <Typography className={classes.boldText}>
                            r/WallStreetBets Reddit Feed
                        </Typography>
                    }/>
                </ListItem>
            </List>
            <Divider/>
            {!loading &&
            posts.map((post) =>
                <ListItem button divider={true} key={post.data.id} onClick={() =>
                    window.open("https://reddit.com" + post.data.permalink, "_blank")}
                >
                    <ListItemText
                        primary={post.data.title}
                        secondary={truncate(post.data.selftext)}
                    />
                </ListItem>
            )
            }
        </div>
    );
}
