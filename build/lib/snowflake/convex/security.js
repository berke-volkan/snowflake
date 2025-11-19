import {query } from "./_generated/server";

export const getKey = query({
  args: {},
  handler: async (ctx) => {
    const key = await ctx.db
      .query("fernet_key")
      .collect();
    return key;
  },
});