const mysql = require("mysql2");

const connection = mysql.createConnection({
  host: "localhost",
  user: "adept",
  database: "diplo",
  password: "3101"
});

connection.connect(function(err) {
  if (err) {
    return console.error("Error:", err.message);
  } else {
    console.log("Connection success\n");
  }
});
